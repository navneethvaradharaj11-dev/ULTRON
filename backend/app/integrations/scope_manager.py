import logging
from typing import Dict, Any, List

logger = logging.getLogger("ULTRON.Integrations.ScopeManager")


class ScopeManager:
    """Manages granular integration permission scopes and maps operational risk levels."""

    SCOPES: Dict[str, Dict[str, str]] = {
        "github": {
            "READ_REPOSITORY": "LOW",
            "READ_ISSUES": "LOW",
            "CREATE_ISSUE": "MEDIUM",
            "READ_PULL_REQUEST": "LOW",
            "CREATE_PULL_REQUEST": "MEDIUM",
            "CREATE_BRANCH": "MEDIUM",
            "MERGE_PULL_REQUEST": "HIGH",
            "DELETE_REPOSITORY": "CRITICAL"
        },
        "calendar": {
            "READ_EVENTS": "LOW",
            "CREATE_EVENT": "MEDIUM",
            "UPDATE_EVENT": "MEDIUM",
            "DELETE_EVENT": "HIGH"
        },
        "email": {
            "READ_EMAIL": "LOW",
            "SEARCH_EMAIL": "LOW",
            "CREATE_DRAFT": "LOW",
            "SEND_EMAIL": "HIGH",
            "DELETE_EMAIL": "HIGH"
        },
        "filesystem": {
            "READ_WORKSPACE": "LOW",
            "READ_FILE": "LOW",
            "WRITE_FILE": "MEDIUM",
            "CREATE_FILE": "LOW",
            "DELETE_FILE": "HIGH"
        }
    }

    @classmethod
    def get_scope_risk(cls, integration_id: str, scope: str) -> str:
        """Get risk level rating for a given scope."""
        integ_scopes = cls.SCOPES.get(integration_id.lower(), {})
        return integ_scopes.get(scope.upper(), "HIGH")

    @classmethod
    def requires_approval(cls, integration_id: str, scope: str) -> bool:
        """Check if an operation scope requires human approval."""
        risk = cls.get_scope_risk(integration_id, scope)
        return risk in ("HIGH", "CRITICAL")
