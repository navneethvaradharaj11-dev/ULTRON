import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_server_rate_limiter_allows_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
