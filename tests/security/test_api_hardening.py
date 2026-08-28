import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.security.token_blacklist import token_blacklist
from app.security.authentication import create_access_token


def test_token_blacklist_revocation():
    token = create_access_token({"sub": "user_blacklisted_test"})
    assert not token_blacklist.is_token_revoked(token)

    token_blacklist.revoke_token(token)
    assert token_blacklist.is_token_revoked(token)


@pytest.mark.asyncio
async def test_unauthenticated_api_access():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/ultron/status")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_malformed_json_command_payload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = create_access_token({"sub": "test_user_id"})
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        res = await ac.post(
            "/api/v1/ultron/command",
            content="invalid_json{",
            headers=headers
        )
    assert res.status_code in (400, 422)
