import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger("ULTRON.UnifiedSecurityGate")


class UnifiedSecurityError(Exception):
    """Exception raised when unified security gate boundaries are violated."""
    pass


class UnifiedSecurityGate:
    """Unified security gate validating authentication, multi-tenant isolation, capability permissions,
    risk evaluation, and human approval gates across Phase 1–10.
    """

    @staticmethod
    def validate_tenant_access(target_user_id: str, request_user_id: str) -> None:
        if target_user_id != request_user_id:
            raise UnifiedSecurityError(f"ACCESS_DENIED: User '{request_user_id}' cannot access resource owned by '{target_user_id}'")

    @staticmethod
    def evaluate_command_risk(intent_risk: str, requires_approval: bool) -> Tuple[bool, str]:
        if intent_risk == "HIGH" or requires_approval:
            return True, "Operation involves sensitive capabilities requiring human approval."
        return False, "Low-risk operation permitted."
