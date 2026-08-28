import logging
from typing import Dict, Any
from app.autonomy.contracts import PriorityLevel

logger = logging.getLogger("ULTRON.PriorityEngine")


class PriorityEngine:
    """Evaluates event priority based on urgency, importance, confidence, and source reliability."""

    @staticmethod
    def evaluate_priority(event_type: str, importance: str = "MEDIUM", is_critical: bool = False) -> PriorityLevel:
        if is_critical or importance.upper() == "CRITICAL":
            return PriorityLevel.CRITICAL
        elif importance.upper() == "HIGH" or event_type in ("SECURITY_EVENT", "WORKFLOW_FAILED"):
            return PriorityLevel.HIGH
        elif importance.upper() == "LOW":
            return PriorityLevel.LOW
        elif importance.upper() == "INFO":
            return PriorityLevel.INFO
        else:
            return PriorityLevel.MEDIUM
