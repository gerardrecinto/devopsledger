from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_status_ok():
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_has_timestamp():
    response = client.get("/health")
    data = response.json()
    assert "timestamp" in data
    assert data["timestamp"]


def test_health_service_name():
    response = client.get("/health")
    data = response.json()
    assert data["service"] == "devopsledger-api"


def test_health_content_type():
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
