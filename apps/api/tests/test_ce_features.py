import uuid

from app.scoring.risk import score_risk


def test_github_pr_ingestion_creates_decision_record(client):
    resp = client.post(
        "/api/v1/ingest/github/pr",
        json={
            "pull_request": {
                "title": "Scale checkout",
                "number": 17,
                "html_url": "https://github.example.com/platform/infra/pull/17",
                "user": {"login": "gerard"},
                "head": {"sha": "abc123"},
                "body": "Refs PLAT-42\nRollback: revert this PR",
                "changed_files": ["terraform/prod/checkout.tf"],
            },
            "repository": {"full_name": "platform/infra"},
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Scale checkout"
    assert data["repository"] == "platform/infra"
    assert data["pr_number"] == 17
    assert data["jira_issues"] == ["PLAT-42"]
    assert data["rollback_assessment"]["score"] == 100


def test_terraform_plan_ingestion_adds_resources_and_scores_risk(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={
            "title": "Replace database",
            "environment": "production",
            "description": "Rollback: restore snapshot",
        },
    ).json()["id"]

    resp = client.post(
        f"/api/v1/decision-records/{record_id}/terraform-plan",
        json={
            "resource_changes": [
                {
                    "address": "aws_db_instance.primary",
                    "type": "aws_db_instance",
                    "provider_name": "registry.terraform.io/hashicorp/aws",
                    "change": {
                        "actions": ["delete", "create"],
                        "before": {"identifier": "primary"},
                        "after": {"identifier": "primary"},
                    },
                }
            ]
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["changed_resources"][0]["address"] == "aws_db_instance.primary"
    assert data["risk_assessment"]["severity"] in {"high", "critical"}
    assert "production environment" in data["risk_assessment"]["reasons"]


def test_argocd_ingestion_records_deployment_event(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={"title": "Deploy payment", "commit_sha": "deadbeef"},
    ).json()["id"]

    resp = client.post(
        "/api/v1/ingest/argocd",
        json={
            "decision_record_id": record_id,
            "app": {
                "metadata": {"name": "payment-api"},
                "spec": {"destination": {"namespace": "production"}},
                "status": {
                    "operationState": {"phase": "Succeeded"},
                    "sync": {"revision": "deadbeef"},
                },
            },
        },
    )

    assert resp.status_code == 201
    assert resp.json()["deployment_events"][0]["app_name"] == "payment-api"


def test_argocd_ingestion_tolerates_null_sections(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={"title": "Deploy search", "commit_sha": "cafe1234"},
    ).json()["id"]

    resp = client.post(
        "/api/v1/ingest/argocd",
        json={
            "decision_record_id": record_id,
            "app": {
                "metadata": {"name": "search-api"},
                "spec": None,
                "status": {"operationState": None, "sync": {"revision": "cafe1234"}},
            },
        },
    )

    assert resp.status_code == 201
    assert resp.json()["deployment_events"][0]["app_name"] == "search-api"


def test_generic_incident_webhook_tolerates_malformed_timestamp(client):
    client.post(
        "/api/v1/decision-records",
        json={
            "title": "Rotate certs",
            "service_name": "edge-proxy",
            "environment": "production",
        },
    )
    resp = client.post(
        "/api/v1/ingest/incidents/generic",
        json={
            "title": "Edge proxy down",
            "service_name": "edge-proxy",
            "environment": "production",
            "started_at": "yesterday-ish",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["correlated_count"] == 1


def test_generic_incident_webhook_correlates_by_service_and_environment(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={
            "title": "Tune payment workers",
            "service_name": "payment-api",
            "environment": "production",
        },
    ).json()["id"]

    resp = client.post(
        "/api/v1/ingest/incidents/generic",
        json={
            "title": "Payment API latency",
            "service_name": "payment-api",
            "environment": "production",
            "severity": "sev2",
            "url": "https://incident.local/1",
        },
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["correlated_count"] == 1
    assert data["correlations"][0]["decision_record_id"] == record_id
    assert data["correlations"][0]["confidence"] == "likely"


def test_dashboard_and_resource_timeline(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={"title": "Change redis", "service_name": "cache"},
    ).json()["id"]
    client.post(
        f"/api/v1/decision-records/{record_id}/terraform-plan",
        json={
            "resource_changes": [
                {
                    "address": "aws_elasticache_cluster.cache",
                    "type": "aws_elasticache_cluster",
                    "provider_name": "aws",
                    "change": {"actions": ["update"], "before": {}, "after": {}},
                }
            ]
        },
    )

    dashboard = client.get("/api/v1/dashboard").json()
    assert dashboard["decision_records"] == 1
    assert dashboard["changed_resources"] == 1

    timeline = client.get("/api/v1/resources/timeline").json()
    assert timeline[0]["address"] == "aws_elasticache_cluster.cache"


def test_missing_record_for_plan_returns_404(client):
    resp = client.post(f"/api/v1/decision-records/{uuid.uuid4()}/terraform-plan", json={})
    assert resp.status_code == 404


def test_risk_scoring_uses_yaml_rules(tmp_path):
    config = tmp_path / "risk-rules.yaml"
    config.write_text("resource_type_weights:\n  custom_resource: 80\n")

    result = score_risk(
        environment="dev",
        changed_resources=[
            {
                "resource_type": "custom_resource",
                "address": "custom_resource.main",
                "actions": ["update"],
            }
        ],
        config_path=str(config),
    )

    assert result["score"] == 95
    assert result["severity"] == "critical"
