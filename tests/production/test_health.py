import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "12.0.0"
    assert "database" in data


def test_liveness_probe_endpoint():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "live"


def test_readiness_probe_endpoint():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
