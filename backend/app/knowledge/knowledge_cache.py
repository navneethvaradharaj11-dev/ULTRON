import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ULTRON.KnowledgeCache")

# Memory cache for source hash + parser version
_CACHE: Dict[str, Dict[str, Any]] = {}
PARSER_VERSION = "1.0.0"


class KnowledgeCache:
    """Caching layer avoiding redundant re-parsing if content hash and parser version are unchanged."""

    @staticmethod
    def get_cached_parsed(content_hash: str) -> Optional[Dict[str, Any]]:
        key = f"{content_hash}_{PARSER_VERSION}"
        if key in _CACHE:
            logger.info("KnowledgeCache HIT for hash '%s'", content_hash)
            return _CACHE[key]
        return None

    @staticmethod
    def set_cached_parsed(content_hash: str, parsed_data: Dict[str, Any]) -> None:
        key = f"{content_hash}_{PARSER_VERSION}"
        _CACHE[key] = parsed_data

    @staticmethod
    def invalidate(content_hash: str) -> None:
        key = f"{content_hash}_{PARSER_VERSION}"
        _CACHE.pop(key, None)
