import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_feedback_submission_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register & login user to obtain token
        await ac.post("/api/v1/auth/register", json={
            "username": "feedback_test_user",
            "email": "feedback_test_user@ultron.ai",
            "password": "SecretPassword123"
        })
        login_res = await ac.post("/api/v1/auth/login", data={
            "username": "feedback_test_user",
            "password": "SecretPassword123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Submit feedback
        res = await ac.post("/api/v1/feedback", json={
            "category": "BUG",
            "description": "UI loading indicator froze during research workflow step.",
            "correlation_id": "req-991823"
        }, headers=headers)

        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "RECEIVED"
        assert data["ticket_id"].startswith("fbk-")
