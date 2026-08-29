import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_correlation_id_header_propagation():
    response = client.get("/api/v1/health")
    assert "X-Correlation-ID" in response.headers
    assert response.headers["X-Correlation-ID"].startswith("req-")


def test_prometheus_metrics_exposition_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ultron_requests_total" in response.text
    assert "ultron_workflows_active" in response.text
