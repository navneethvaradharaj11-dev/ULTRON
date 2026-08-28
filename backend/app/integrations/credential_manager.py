import base64
import hashlib
import logging
from typing import Dict, Any, Optional, List
from app.integrations.contracts import IntegrationCredential

logger = logging.getLogger("ULTRON.Integrations.CredentialManager")


class CredentialManager:
    """Manages encrypted OAuth tokens, refresh tokens, and API keys with multi-tenant isolation and secret masking."""

    def __init__(self, secret_key: str = "ULTRON_INTEGRATION_KEY_ENCRYPTION_SALT"):
        self._key = hashlib.sha256(secret_key.encode()).digest()
        self._credentials: Dict[str, IntegrationCredential] = {}

    def _make_key(self, user_id: str, integration_id: str) -> str:
        return f"{user_id}:{integration_id.lower()}"

    def save_credential(self, credential: IntegrationCredential) -> None:
        """Store integration credential for user."""
        key = self._make_key(credential.user_id, credential.integration_id)
        # Encrypt sensitive tokens in memory structure
        encrypted_cred = IntegrationCredential(
            integration_id=credential.integration_id,
            user_id=credential.user_id,
            access_token=self._encrypt(credential.access_token) if credential.access_token else None,
            refresh_token=self._encrypt(credential.refresh_token) if credential.refresh_token else None,
            api_key=self._encrypt(credential.api_key) if credential.api_key else None,
            expires_at=credential.expires_at,
            scopes=credential.scopes
        )
        self._credentials[key] = encrypted_cred
        logger.info("Saved encrypted credentials for user '%s' on integration '%s'", credential.user_id, credential.integration_id)

    def get_decrypted_credential(self, user_id: str, integration_id: str) -> Optional[IntegrationCredential]:
        """Retrieve and decrypt integration credential for authorized user."""
        key = self._make_key(user_id, integration_id)
        cred = self._credentials.get(key)
        if not cred:
            return None

        return IntegrationCredential(
            integration_id=cred.integration_id,
            user_id=cred.user_id,
            access_token=self._decrypt(cred.access_token) if cred.access_token else None,
            refresh_token=self._decrypt(cred.refresh_token) if cred.refresh_token else None,
            api_key=self._decrypt(cred.api_key) if cred.api_key else None,
            expires_at=cred.expires_at,
            scopes=cred.scopes
        )

    def revoke_credential(self, user_id: str, integration_id: str) -> None:
        """Revoke credentials for specified tenant."""
        key = self._make_key(user_id, integration_id)
        if key in self._credentials:
            del self._credentials[key]
            logger.info("Revoked integration credentials for user '%s' on '%s'", user_id, integration_id)

    def _encrypt(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        # XOR + Base64 deterministic encryption for local sandbox isolation
        b_text = text.encode()
        encrypted = bytes([b ^ self._key[i % len(self._key)] for i, b in enumerate(b_text)])
        return base64.b64encode(encrypted).decode()

    def _decrypt(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        raw = base64.b64decode(text.encode())
        decrypted = bytes([b ^ self._key[i % len(self._key)] for i, b in enumerate(raw)])
        return decrypted.decode(errors="replace")


# Global singleton instance
credential_manager = CredentialManager()
