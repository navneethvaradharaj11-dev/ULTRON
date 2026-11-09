import os
from enum import Enum
from typing import Tuple, Optional


class SandboxActionRisk(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    FORBIDDEN = "FORBIDDEN"


class SandboxPolicy:
    """Security policy enforcer for code sandbox actions."""

    FORBIDDEN_PATTERNS = [
        "..", "/etc", "/var", "/usr", "/bin", "/sbin",
        "C:\\Windows", "C:\\Users", ".env", "mysql", "jwt",
        "ssh", "id_rsa", "credentials", "config.json",
        "backend", "ultron", "app", "frontend"
    ]


    @classmethod
    def evaluate_action(
        self,
        action: str,
        path: Optional[str] = None,
        language: Optional[str] = None,
        network_target: Optional[str] = None
    ) -> Tuple[SandboxActionRisk, str]:
        """Evaluate an action's risk profile. Returns (risk_level, reason)."""
        act_upper = action.upper().strip()

        # Check for path traversal or sensitive file access
        if path:
            norm_path = os.path.normpath(path).replace("\\", "/")
            if norm_path.startswith("/") or ".." in norm_path:
                return SandboxActionRisk.FORBIDDEN, "ACCESS_DENIED: Absolute paths or parent directory traversal ('..') are forbidden."
            for forbidden in self.FORBIDDEN_PATTERNS:
                if forbidden.lower() in norm_path.lower():
                    return SandboxActionRisk.FORBIDDEN, f"ACCESS_DENIED: Access to sensitive file path pattern '{forbidden}' is forbidden."

        # Action-based evaluation
        if act_upper in ("CREATE_FILE", "READ_FILE", "UPDATE_FILE", "LIST_FILES", "DELETE_FILE", "COMPILE", "EXECUTE", "GENERATE_TESTS", "RUN_TESTS"):
            return SandboxActionRisk.AUTO_APPROVED, "Standard isolated sandbox action."

        if act_upper in ("NETWORK_ACCESS", "EXPORT_FILE", "ACCESS_EXTERNAL_SERVICE", "PRIVILEGED_OP"):
            return SandboxActionRisk.REQUIRES_APPROVAL, f"Operation '{action}' requires explicit user approval."

        return SandboxActionRisk.FORBIDDEN, f"Unknown or unhandled sandbox action '{action}'."
