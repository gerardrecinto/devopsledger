import uuid


def test_list_empty(client):
    resp = client.get("/api/v1/decision-records")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_returns_201(client):
    resp = client.post("/api/v1/decision-records", json={"title": "Deploy ECS service"})
    assert resp.status_code == 201


def test_create_fields(client):
    resp = client.post(
        "/api/v1/decision-records",
        json={
            "title": "Scale Kafka brokers",
            "environment": "production",
            "service_name": "kafka",
            "author": "gerard",
            "status": "open",
        },
    )
    data = resp.json()
    assert data["title"] == "Scale Kafka brokers"
    assert data["environment"] == "production"
    assert data["service_name"] == "kafka"
    assert data["author"] == "gerard"
    assert data["status"] == "open"
    assert "id" in data
    assert "created_at" in data


def test_create_default_status(client):
    resp = client.post("/api/v1/decision-records", json={"title": "No status set"})
    assert resp.json()["status"] == "open"


def test_get_by_id(client):
    record_id = client.post(
        "/api/v1/decision-records", json={"title": "Get me"}
    ).json()["id"]
    resp = client.get(f"/api/v1/decision-records/{record_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == record_id


def test_get_not_found(client):
    missing = str(uuid.uuid4())
    resp = client.get(f"/api/v1/decision-records/{missing}")
    assert resp.status_code == 404


def test_list_returns_created(client):
    client.post("/api/v1/decision-records", json={"title": "A"})
    client.post("/api/v1/decision-records", json={"title": "B"})
    resp = client.get("/api/v1/decision-records")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_fields(client):
    record_id = client.post(
        "/api/v1/decision-records", json={"title": "Before"}
    ).json()["id"]
    resp = client.patch(
        f"/api/v1/decision-records/{record_id}",
        json={"title": "After", "status": "deployed"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "After"
    assert data["status"] == "deployed"


def test_update_can_clear_nullable_field(client):
    record_id = client.post(
        "/api/v1/decision-records",
        json={"title": "Keep title", "description": "stale context"},
    ).json()["id"]
    resp = client.patch(
        f"/api/v1/decision-records/{record_id}",
        json={"description": None},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] is None
    assert resp.json()["title"] == "Keep title"


def test_update_rejects_null_title(client):
    record_id = client.post(
        "/api/v1/decision-records", json={"title": "Required"}
    ).json()["id"]
    resp = client.patch(
        f"/api/v1/decision-records/{record_id}",
        json={"title": None},
    )
    assert resp.status_code == 422


def test_update_not_found(client):
    resp = client.patch(
        f"/api/v1/decision-records/{uuid.uuid4()}",
        json={"title": "Ghost"},
    )
    assert resp.status_code == 404


def test_delete(client):
    record_id = client.post(
        "/api/v1/decision-records", json={"title": "Delete me"}
    ).json()["id"]
    del_resp = client.delete(f"/api/v1/decision-records/{record_id}")
    assert del_resp.status_code == 204
    get_resp = client.get(f"/api/v1/decision-records/{record_id}")
    assert get_resp.status_code == 404


def test_delete_not_found(client):
    resp = client.delete(f"/api/v1/decision-records/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_delete_removes_from_list(client):
    record_id = client.post(
        "/api/v1/decision-records", json={"title": "Gone"}
    ).json()["id"]
    client.delete(f"/api/v1/decision-records/{record_id}")
    items = client.get("/api/v1/decision-records").json()
    assert all(r["id"] != record_id for r in items)
