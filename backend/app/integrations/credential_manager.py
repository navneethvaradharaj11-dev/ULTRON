import os
import json
import base64
import hashlib
import logging
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet, InvalidToken
from app.integrations.contracts import IntegrationCredential
from app.config.settings import settings

logger = logging.getLogger("ULTRON.Integrations.CredentialManager")


class CredentialManager:
    """Manages encrypted OAuth tokens, refresh tokens, and API keys using AES-256 Fernet encryption,
    multi-tenant isolation, and persistent store sync.
    """

    def __init__(self, secret_key: Optional[str] = None):
        key_source = secret_key or getattr(settings, "JWT_SECRET", "ULTRON_INTEGRATION_KEY_ENCRYPTION_SALT")
        key_bytes = hashlib.sha256(key_source.encode()).digest()
        self._fernet_key = base64.urlsafe_b64encode(key_bytes)
        self._fernet = Fernet(self._fernet_key)
        self._legacy_key = key_bytes
        self._credentials: Dict[str, IntegrationCredential] = {}
        self._persistence_file = os.path.join(os.path.dirname(__file__), "../../database/credentials_store.json")
        self._load_local_store()

    def _make_key(self, user_id: str, integration_id: str) -> str:
        return f"{user_id}:{integration_id.lower()}"

    def _load_local_store(self) -> None:
        try:
            if os.path.exists(self._persistence_file):
                with open(self._persistence_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    self._credentials[k] = IntegrationCredential(**v)
        except Exception as e:
            logger.warning("Could not load local credential store: %s", e)

    def _save_local_store(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._persistence_file), exist_ok=True)
            data = {k: (v.model_dump() if hasattr(v, "model_dump") else v.dict()) for k, v in self._credentials.items()}
            with open(self._persistence_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Could not save local credential store: %s", e)


    def save_credential(self, credential: IntegrationCredential) -> None:
        """Store integration credential for user with AES-256 encryption and persistence."""
        key = self._make_key(credential.user_id, credential.integration_id)
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
        self._save_local_store()
        logger.info("Saved encrypted credentials for user '%s' on integration '%s'", credential.user_id, credential.integration_id)

    async def save_credential_async(self, credential: IntegrationCredential, db: Any) -> None:
        """Store credential in both local store and MySQL database via IntegrationRepository."""
        self.save_credential(credential)
        try:
            from app.database.repositories.integration_repo import IntegrationRepository
            repo = IntegrationRepository(db)
            key = self._make_key(credential.user_id, credential.integration_id)
            enc = self._credentials[key]
            await repo.save_credential(
                user_id=credential.user_id,
                integration_id=credential.integration_id,
                encrypted_access_token=enc.access_token,
                encrypted_refresh_token=enc.refresh_token,
                encrypted_api_key=enc.api_key,
                expires_at=credential.expires_at,
                scopes=credential.scopes
            )
        except Exception as e:
            logger.warning("Database credential save fallback: %s", e)

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

    async def get_decrypted_credential_async(self, user_id: str, integration_id: str, db: Any) -> Optional[IntegrationCredential]:
        """Retrieve credential with DB read-through on local store miss."""
        cred = self.get_decrypted_credential(user_id, integration_id)
        if cred:
            return cred
        try:
            from app.database.repositories.integration_repo import IntegrationRepository
            repo = IntegrationRepository(db)
            db_cred = await repo.get_credential(user_id, integration_id)
            if db_cred:
                mem_cred = IntegrationCredential(
                    integration_id=db_cred.integration_id,
                    user_id=db_cred.user_id,
                    access_token=db_cred.encrypted_access_token,
                    refresh_token=db_cred.encrypted_refresh_token,
                    api_key=db_cred.encrypted_api_key,
                    expires_at=db_cred.expires_at.isoformat() if db_cred.expires_at else None,
                    scopes=db_cred.scopes_json
                )
                key = self._make_key(user_id, integration_id)
                self._credentials[key] = mem_cred
                return self.get_decrypted_credential(user_id, integration_id)
        except Exception as e:
            logger.warning("Database credential fetch fallback: %s", e)
        return None

    def revoke_credential(self, user_id: str, integration_id: str) -> None:
        """Revoke credentials for specified tenant."""
        key = self._make_key(user_id, integration_id)
        if key in self._credentials:
            del self._credentials[key]
            self._save_local_store()
            logger.info("Revoked integration credentials for user '%s' on '%s'", user_id, integration_id)

    def _encrypt(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        return self._fernet.encrypt(text.encode()).decode()

    def _decrypt(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        try:
            return self._fernet.decrypt(text.encode()).decode()
        except (InvalidToken, Exception):
            # Fallback to legacy XOR decryption for backward compatibility
            try:
                raw = base64.b64decode(text.encode())
                decrypted = bytes([b ^ self._legacy_key[i % len(self._legacy_key)] for i, b in enumerate(raw)])
                return decrypted.decode(errors="replace")
            except Exception:
                return None


# Global singleton instance
credential_manager = CredentialManager()

