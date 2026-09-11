import pytest
from app.security.token_manager import token_manager


def test_token_issuance_rotation_and_revocation():
    payload = {"sub": "usr-test-123"}
    access_token = token_manager.create_access_token(payload)
    refresh_token = token_manager.create_refresh_token(payload)

    assert access_token is not None
    assert refresh_token is not None

    decoded = token_manager.decode_token(access_token)
    assert decoded["sub"] == "usr-test-123"

    # Revoke access token
    token_manager.revoke_token(access_token)
    assert token_manager.is_token_revoked(access_token)
    assert token_manager.decode_token(access_token) is None


def test_login_brute_force_rate_limiter():
    user_id = "attacker@test.internal"
    for _ in range(5):
        token_manager.record_login_attempt(user_id)

    allowed = token_manager.check_login_rate_limit(user_id, max_attempts=5, window_seconds=60)
    assert allowed is False
