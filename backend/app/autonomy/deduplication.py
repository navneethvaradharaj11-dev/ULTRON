import hashlib
import logging
from typing import Set, Dict, Any

logger = logging.getLogger("ULTRON.AutonomyDeduplication")

_SEEN_DEDUP_KEYS: Set[str] = set()


class DeduplicationManager:
    """Manages SHA-256 event deduplication preventing duplicate event processing."""

    @staticmethod
    def generate_key(user_id: str, event_type: str, source: str, raw_content: str) -> str:
        data = f"{user_id}_{event_type}_{source}_{raw_content}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def is_duplicate(dedup_key: str) -> bool:
        if dedup_key in _SEEN_DEDUP_KEYS:
            logger.info("Event deduplication key '%s' already seen, skipping.", dedup_key[:12])
            return True
        _SEEN_DEDUP_KEYS.add(dedup_key)
        return False
