from app.integrations.argocd.parser import parse_sync_event
from app.integrations.github.parser import (
    check_codeowners_approval,
    parse_codeowners_review,
    parse_jira_issue_keys,
    parse_pr_event,
)
from app.integrations.pagerduty.parser import parse_incident_webhook
from app.integrations.terraform.parser import parse_plan


# ── GitHub ────────────────────────────────────────────────────────────────────

def test_github_pr_title():
    payload = {
        "pull_request": {"title": "Add ECS scaling", "number": 42,
                         "html_url": "https://github.com/org/repo/pull/42",
                         "user": {"login": "gerard"}, "head": {"sha": "abc123"},
                         "body": "Scales the ECS service"},
        "repository": {"full_name": "org/repo"},
    }
    result = parse_pr_event(payload)
    assert result["title"] == "Add ECS scaling"
    assert result["pr_number"] == 42
    assert result["author"] == "gerard"
    assert result["repository"] == "org/repo"
    assert result["commit_sha"] == "abc123"


def test_github_pr_missing_fields():
    result = parse_pr_event({})
    assert result["title"] == ""
    assert result["pr_number"] is None
    assert result["author"] is None


def test_github_codeowners_approved():
    review = {"user": {"login": "alice"}, "state": "approved", "body": "LGTM"}
    result = parse_codeowners_review(review)
    assert result["approved"] is True
    assert result["approver"] == "alice"
    assert result["source"] == "github_codeowners"


def test_github_codeowners_rejected():
    review = {"user": {"login": "bob"}, "state": "changes_requested", "body": "Needs work"}
    result = parse_codeowners_review(review)
    assert result["approved"] is False


def test_jira_issue_key_parsing():
    assert parse_jira_issue_keys("Refs PLAT-42 and SRE-7") == ["PLAT-42", "SRE-7"]


def test_codeowners_approval_check_matches_owner_review():
    codeowners = """
    * @platform/team
    terraform/prod/* @alice @bob
    """
    result = check_codeowners_approval(
        changed_files=["terraform/prod/api.tf"],
        codeowners_text=codeowners,
        reviews=[{"user": {"login": "alice"}, "state": "APPROVED"}],
    )
    assert result["required"] is True
    assert result["approved"] is True
    assert result["owner"] == "alice"


def test_codeowners_approval_check_missing_owner_review():
    result = check_codeowners_approval(
        changed_files=["terraform/prod/api.tf"],
        codeowners_text="terraform/prod/* @alice",
        reviews=[{"user": {"login": "mallory"}, "state": "APPROVED"}],
    )
    assert result["required"] is True
    assert result["approved"] is False


# ── Terraform ─────────────────────────────────────────────────────────────────

def test_terraform_create():
    plan = {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.logs",
                "type": "aws_s3_bucket",
                "provider_name": "registry.terraform.io/hashicorp/aws",
                "change": {"actions": ["create"], "before": None,
                            "after": {"bucket": "my-logs"}},
            }
        ]
    }
    result = parse_plan(plan)
    assert len(result) == 1
    assert result[0]["address"] == "aws_s3_bucket.logs"
    assert result[0]["actions"] == ["create"]
    assert result[0]["provider"] == "aws"
    assert result[0]["before_summary"] is None
    assert result[0]["after_summary"] == {"bucket": "my-logs"}


def test_terraform_skips_no_op():
    plan = {
        "resource_changes": [
            {"address": "aws_s3_bucket.x", "type": "aws_s3_bucket",
             "provider_name": "aws",
             "change": {"actions": ["no-op"], "before": {}, "after": {}}},
        ]
    }
    assert parse_plan(plan) == []


def test_terraform_skips_read():
    plan = {
        "resource_changes": [
            {"address": "data.aws_ami.x", "type": "aws_ami",
             "provider_name": "aws",
             "change": {"actions": ["read"], "before": None, "after": {}}},
        ]
    }
    assert parse_plan(plan) == []


def test_terraform_strips_tags_all():
    plan = {
        "resource_changes": [
            {"address": "aws_instance.web", "type": "aws_instance",
             "provider_name": "aws",
             "change": {"actions": ["update"],
                        "before": {"instance_type": "t3.small", "tags_all": {"env": "prod"}},
                        "after": {"instance_type": "t3.medium", "tags_all": {"env": "prod"}}}},
        ]
    }
    result = parse_plan(plan)
    assert "tags_all" not in result[0]["before_summary"]
    assert result[0]["before_summary"]["instance_type"] == "t3.small"


def test_terraform_empty_plan():
    assert parse_plan({}) == []
    assert parse_plan({"resource_changes": []}) == []


# ── Argo CD ───────────────────────────────────────────────────────────────────

def test_argocd_sync_event():
    payload = {
        "app": {
            "metadata": {"name": "payment-api"},
            "spec": {"destination": {"namespace": "production"}},
            "status": {
                "operationState": {"phase": "Succeeded"},
                "sync": {"revision": "deadbeef"},
            },
        }
    }
    result = parse_sync_event(payload)
    assert result["source"] == "argocd"
    assert result["app_name"] == "payment-api"
    assert result["environment"] == "production"
    assert result["status"] == "Succeeded"
    assert result["revision"] == "deadbeef"


def test_argocd_empty_payload():
    result = parse_sync_event({})
    assert result["source"] == "argocd"
    assert result["app_name"] is None


# ── PagerDuty ─────────────────────────────────────────────────────────────────

def test_pagerduty_single_event():
    payload = {
        "events": [
            {
                "event_type": "incident.triggered",
                "data": {
                    "title": "High CPU on prod",
                    "html_url": "https://app.pagerduty.com/incidents/ABC",
                    "severity": "critical",
                    "created_at": "2026-05-24T10:00:00Z",
                    "service": {"summary": "Payment Service"},
                },
            }
        ]
    }
    results = parse_incident_webhook(payload)
    assert len(results) == 1
    r = results[0]
    assert r["incident_source"] == "pagerduty"
    assert r["incident_title"] == "High CPU on prod"
    assert r["severity"] == "critical"
    assert r["service_name"] == "Payment Service"
    assert r["confidence"] == "possible"


def test_pagerduty_multiple_events():
    payload = {
        "events": [
            {"event_type": "incident.triggered",
             "data": {"title": "Event 1", "service": {}}},
            {"event_type": "incident.resolved",
             "data": {"title": "Event 2", "service": {}}},
        ]
    }
    results = parse_incident_webhook(payload)
    assert len(results) == 2


def test_pagerduty_empty_events():
    results = parse_incident_webhook({"events": []})
    assert results == []
