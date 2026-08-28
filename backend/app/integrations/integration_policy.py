import logging
from typing import Tuple, Dict, Any, Optional
from app.integrations.scope_manager import ScopeManager

logger = logging.getLogger("ULTRON.Integrations.Policy")


class IntegrationPolicy:
    """Security policy validator enforcing scope checks, risk thresholds, and approval requirements."""

    @classmethod
    def evaluate_operation_policy(
        cls,
        integration_id: str,
        operation_id: str,
        required_scopes: list,
        granted_scopes: list
    ) -> Tuple[bool, bool, str]:
        """Returns (is_allowed, requires_approval, reason)."""
        # 1. Scope Validation
        for req_scope in required_scopes:
            if req_scope not in granted_scopes:
                return False, False, f"SCOPE_DENIED: Required scope '{req_scope}' not granted to user."

        # 2. Risk & Approval Check
        needs_approval = False
        for req_scope in required_scopes:
            if ScopeManager.requires_approval(integration_id, req_scope):
                needs_approval = True
                break

        return True, needs_approval, "Operation authorized by policy."
