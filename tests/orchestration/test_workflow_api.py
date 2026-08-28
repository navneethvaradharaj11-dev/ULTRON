import pytest
from starlette.testclient import TestClient
from app.main import app

def test_workflow_api_unauthorized_access():
    client = TestClient(app)
    res = client.get("/api/v1/workflows")
    assert res.status_code == 401
