import logging
from datetime import datetime
from typing import Dict, Any, Optional
from app.intelligence.secret_detector import SecretDetector

logger = logging.getLogger(__name__)

class FailureManager:
    """Failure Manager for classifying and contextualizing workflow execution failures."""

    FAILURE_TYPES = {
        "TRANSIENT",
        "TIMEOUT",
        "TOOL_FAILURE",
        "AGENT_FAILURE",
        "VALIDATION_FAILURE",
        "SECURITY_FAILURE",
        "APPROVAL_REQUIRED",
        "RESOURCE_LIMIT",
        "DEPENDENCY_FAILURE",
        "UNKNOWN"
    }

    @classmethod
    def classify_failure(cls, exception_or_msg: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg = str(exception_or_msg)
        lower_msg = msg.lower()

        if "timeout" in lower_msg:
            ftype = "TIMEOUT"
            recoverable = True
        elif "security" in lower_msg or "access denied" in lower_msg or "unauthorized" in lower_msg:
            ftype = "SECURITY_FAILURE"
            recoverable = False
        elif "approval" in lower_msg or "requires_approval" in lower_msg:
            ftype = "APPROVAL_REQUIRED"
            recoverable = True
        elif "quota" in lower_msg or "limit exceeded" in lower_msg:
            ftype = "RESOURCE_LIMIT"
            recoverable = False
        elif "compile" in lower_msg or "syntax" in lower_msg or "test failed" in lower_msg:
            ftype = "VALIDATION_FAILURE"
            recoverable = True
        elif "connection" in lower_msg or "network" in lower_msg:
            ftype = "TRANSIENT"
            recoverable = True
        else:
            ftype = "AGENT_FAILURE"
            recoverable = True

        # Sanitize error message and context to prevent secret leakage
        clean_msg = SecretDetector.sanitize_text(msg)
        clean_context = {}
        if context:
            for k, v in context.items():
                if isinstance(v, str):
                    clean_context[k] = SecretDetector.sanitize_text(v)
                else:
                    clean_context[k] = v

        return {
            "failure_type": ftype,
            "error_message": clean_msg,
            "recoverable": recoverable,
            "context": clean_context,
            "timestamp": datetime.utcnow().isoformat()
        }
