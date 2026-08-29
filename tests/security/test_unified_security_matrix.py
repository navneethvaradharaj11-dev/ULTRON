import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.security.token_manager import TokenManager
from app.security.browser_security import BrowserSecurity
from app.sandbox.filesystem import SandboxFilesystem
from app.sandbox.sandbox_policy import SandboxPolicy, SandboxActionRisk
from app.integrations.credential_manager import CredentialManager


@pytest.mark.asyncio
async def test_unified_security_matrix_all_16_controls(tmp_path):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Authentication & Unauthorized Access
        res_unauth = await ac.get("/api/v1/ultron/status")
        assert res_unauth.status_code == 401, "Unauthenticated access must return 401"

        # Register User A and User B for tenant isolation tests
        await ac.post("/api/v1/auth/register", json={
            "username": "sec_user_a",
            "email": "user_a@ultron.ai",
            "password": "Password123!"
        })
        await ac.post("/api/v1/auth/register", json={
            "username": "sec_user_b",
            "email": "user_b@ultron.ai",
            "password": "Password123!"
        })

        login_a = await ac.post("/api/v1/auth/login", data={"username": "sec_user_a", "password": "Password123!"})
        login_b = await ac.post("/api/v1/auth/login", data={"username": "sec_user_b", "password": "Password123!"})

        token_a = login_a.json()["access_token"]
        token_b = login_b.json()["access_token"]

        headers_a = {"Authorization": f"Bearer {token_a}"}

        # 2. JWT Verification & Forgery Rejection
        res_forged = await ac.get("/api/v1/ultron/status", headers={"Authorization": "Bearer forged.jwt.token"})
        assert res_forged.status_code == 401, "Forged JWT must be rejected with 401"

        # 3. Tenant Isolation
        res_status_a = await ac.get("/api/v1/ultron/status", headers=headers_a)
        assert res_status_a.status_code == 200, "Authenticated user A must access their own status"

        # 4. SSRF Prevention
        ssrf_res = BrowserSecurity.validate_url("http://169.254.169.254/latest/meta-data")
        assert ssrf_res is False, "Metadata endpoint access must be blocked by SSRF filter"

        # 5. Sandbox Path Traversal Rejection
        fs = SandboxFilesystem("sec_exec_1", base_dir=str(tmp_path))
        with pytest.raises(ValueError, match="ACCESS_DENIED"):
            fs.resolve_path("../../etc/passwd")

        # 6. Sandbox Policy Risk Evaluation
        risk, reason = SandboxPolicy.evaluate_action("READ_FILE", path="../.env")
        assert risk == SandboxActionRisk.FORBIDDEN

        # 7. Secret Redaction & Leakage Prevention
        from app.intelligence.secret_detector import SecretDetector
        sanitized = SecretDetector.sanitize("User password is password = 'SuperSecretPassword123'")
        assert "[REDACTED_" in sanitized, "Secret key must be redacted"
        assert "SuperSecretPassword123" not in sanitized, "Plaintext secret must not remain"

        # 8. Token Blacklisting & Revocation
        tm = TokenManager()
        tm.revoke_token(token_a)
        is_blacklisted = tm.is_token_revoked(token_a)
        assert is_blacklisted is True, "Revoked token must be blacklisted"

        # 9. Credential AES-256 Encryption
        cm = CredentialManager()
        enc = cm._encrypt("db_secret_pass")
        dec = cm._decrypt(enc)
        assert dec == "db_secret_pass", "AES-256 encryption/decryption must be symmetric"
        assert enc != "db_secret_pass", "Plaintext must not be exposed in ciphertext"

        # 10. Webhook Signature Verification
        from app.integrations.webhook_manager import WebhookManager
        sig_valid = WebhookManager.verify_signature(b"payload", "sha256=invalid_sig", "secret")
        assert sig_valid is False, "Invalid webhook signature must be rejected"

        # 11. Rate Limiting Gate
        res_health = await ac.get("/health/live")
        assert res_health.status_code == 200, "Health probe must be unthrottled"
