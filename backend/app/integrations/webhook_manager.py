import hmac
import hashlib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ULTRON.Integrations.WebhookManager")


class WebhookManager:
    """Manages incoming integration webhooks, signature verification, and deduplication."""

    @staticmethod
    def verify_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
        """Verify HMAC-SHA256 signature for incoming webhook payloads."""
        if not signature or not secret:
            return False
        expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
        clean_sig = signature.replace("sha256=", "").strip()
        return hmac.compare_digest(expected, clean_sig)

    @staticmethod
    def compute_event_hash(provider: str, event_type: str, payload_json: Dict[str, Any]) -> str:
        """Generate deterministic SHA-256 hash for deduplication."""
        raw = f"{provider}:{event_type}:{str(payload_json)}"
        return hashlib.sha256(raw.encode()).hexdigest()
