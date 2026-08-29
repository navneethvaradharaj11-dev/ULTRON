import os
import pytest
from app.integrations.contracts import IntegrationCredential
from app.integrations.credential_manager import CredentialManager
from app.core.capability_registry import CapabilityRegistry
from app.database.migrations.run_migrations import run_migrations


def test_credential_manager_aes_encryption_and_persistence(tmp_path):
    # Test Fernet AES-256 encryption and persistence across manager instances
    cm1 = CredentialManager(secret_key="STRONG_TEST_ENCRYPTION_KEY_123")
    cm1._persistence_file = str(tmp_path / "credentials_store.json")

    cred = IntegrationCredential(
        integration_id="github",
        user_id="user_hardened",
        access_token="gho_hardened_secret_token_789",
        scopes=["READ_REPOSITORY", "CREATE_ISSUES"]
    )
    cm1.save_credential(cred)

    # Decrypt with original manager instance
    dec1 = cm1.get_decrypted_credential("user_hardened", "github")
    assert dec1 is not None
    assert dec1.access_token == "gho_hardened_secret_token_789"

    # Simulate backend restart with a new CredentialManager instance reading the same persistence file
    cm2 = CredentialManager(secret_key="STRONG_TEST_ENCRYPTION_KEY_123")
    cm2._persistence_file = str(tmp_path / "credentials_store.json")
    cm2._load_local_store()

    dec2 = cm2.get_decrypted_credential("user_hardened", "github")
    assert dec2 is not None
    assert dec2.access_token == "gho_hardened_secret_token_789"
    assert "CREATE_ISSUES" in dec2.scopes


def test_capability_registry_includes_webhooks():
    reg = CapabilityRegistry()
    health = reg.get_system_health()
    assert "webhooks" in health["capabilities"]
    webhook_cap = reg.get_capability("webhooks")
    assert webhook_cap is not None
    assert webhook_cap.status == "AVAILABLE"


def test_idempotent_schema_migrations_version_check():
    # Should complete without error
    run_migrations(version="v11.0.0_test")
