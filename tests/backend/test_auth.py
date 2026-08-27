import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "registered_tools_count" in data


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register user
        reg_res = await ac.post("/api/v1/auth/register", json={
            "username": "testuser_ultron_unique",
            "email": "testuser_ultron_unique@ultron.ai",
            "password": "SecretPassword123"
        })
        assert reg_res.status_code in [201, 400]

        # Login user
        login_res = await ac.post("/api/v1/auth/login", data={
            "username": "testuser_ultron_unique",
            "password": "SecretPassword123"
        })
        assert login_res.status_code == 200
        tokens = login_res.json()
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"

        # Get me profile
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        me = me_res.json()
        assert me["username"] == "testuser_ultron_unique"
