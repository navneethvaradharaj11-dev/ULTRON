import pytest
from app.integrations.contracts import IntegrationCredential
from app.integrations.credential_manager import CredentialManager


def test_credential_encryption_decryption():
    cm = CredentialManager()
    cred = IntegrationCredential(
        integration_id="github",
        user_id="user_123",
        access_token="gho_secret_access_token_abc123",
        scopes=["READ_REPOSITORY", "READ_ISSUES"]
    )

    cm.save_credential(cred)

    decrypted = cm.get_decrypted_credential("user_123", "github")
    assert decrypted is not None
    assert decrypted.access_token == "gho_secret_access_token_abc123"
    assert "READ_REPOSITORY" in decrypted.scopes


def test_cross_tenant_credential_isolation():
    cm = CredentialManager()
    cred = IntegrationCredential(
        integration_id="github",
        user_id="alice",
        access_token="alice_secret_token"
    )
    cm.save_credential(cred)

    # Bob attempting to read Alice's credentials
    bob_cred = cm.get_decrypted_credential("bob", "github")
    assert bob_cred is None
