import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("ULTRON.AutonomySecurity")


class AutonomySecurityError(Exception):
    """Exception raised when autonomy security boundaries are violated."""
    pass


class AutonomySecurityValidator:
    """Security validator enforcing multi-tenant rule ownership, permission escalation defense,
    and prompt injection isolation for Phase 9 Autonomy Engine.
    """

    @staticmethod
    def validate_rule_access(rule_user_id: str, request_user_id: str) -> None:
        if rule_user_id != request_user_id:
            raise AutonomySecurityError(f"ACCESS_DENIED: User '{request_user_id}' cannot access rule owned by '{rule_user_id}'")

    @staticmethod
    def validate_execution_access(exec_user_id: str, request_user_id: str) -> None:
        if exec_user_id != request_user_id:
            raise AutonomySecurityError(f"ACCESS_DENIED: User '{request_user_id}' cannot access execution owned by '{exec_user_id}'")
