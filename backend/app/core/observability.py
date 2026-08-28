import re
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("ULTRON.Observability")


class ObservabilityLogger:
    """Structured logging and audit layer ensuring observability without secret leakage."""

    SECRET_PATTERNS = [
        re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{12,})['\"]?"),
        re.compile(r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"),
        re.compile(r"(?i)(password|passwd|pwd|db_pass)\s*[:=]\s*['\"]([^'\"]+)['\"]"),
    ]

    @classmethod
    def mask_secrets(cls, text: str) -> str:
        if not text:
            return ""
        sanitized = text
        for pattern in cls.SECRET_PATTERNS:
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)
        return sanitized

    @classmethod
    def log_event(
        cls,
        event_name: str,
        workflow_id: Optional[str] = None,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        status: str = "INFO",
        duration_ms: Optional[int] = None,
        details: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> Dict[str, Any]:
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_name": event_name,
            "workflow_id": workflow_id,
            "user_id": user_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "status": status,
            "duration_ms": duration_ms,
            "error_code": error_code,
            "details": cls.mask_secrets(details or "")
        }
        logger.info("[OBSERVABILITY] %s", json.dumps(payload))
        return payload
