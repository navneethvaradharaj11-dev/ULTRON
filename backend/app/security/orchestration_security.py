import logging
from typing import Dict, Any, Tuple
from app.orchestration.orchestration_policy import OrchestrationPolicy, default_orchestration_policy
from app.intelligence.secret_detector import SecretDetector

logger = logging.getLogger(__name__)

class OrchestrationSecurityError(Exception):
    """Raised when an orchestration security or quota rule is violated."""
    pass

class OrchestrationSecurity:
    """Security and quota enforcement module for Phase 7 Orchestration."""

    def __init__(self, policy: OrchestrationPolicy = default_orchestration_policy):
        self.policy = policy

    def validate_tenant_ownership(self, resource_user_id: str, requesting_user_id: str) -> None:
        """Enforce strict multi-tenant user ownership."""
        if resource_user_id != requesting_user_id:
            logger.warning("Security violation: User %s attempted to access resource belonging to %s", requesting_user_id, resource_user_id)
            raise OrchestrationSecurityError("Access denied: Tenant ownership mismatch")

    def check_task_quota(self, current_task_count: int) -> None:
        """Check maximum workflow task quota."""
        if current_task_count >= self.policy.max_workflow_tasks:
            raise OrchestrationSecurityError(f"Task limit exceeded: {current_task_count} >= {self.policy.max_workflow_tasks}")

    def check_retry_quota(self, current_retry_count: int) -> None:
        """Check maximum workflow retry quota."""
        if current_retry_count >= self.policy.max_workflow_retries:
            raise OrchestrationSecurityError(f"Retry limit exceeded: {current_retry_count} >= {self.policy.max_workflow_retries}")

    def check_replan_quota(self, current_replan_count: int) -> None:
        """Check maximum dynamic replan quota."""
        if current_replan_count >= self.policy.max_replans:
            raise OrchestrationSecurityError(f"Re-plan limit exceeded: {current_replan_count} >= {self.policy.max_replans}")

    def check_duration(self, elapsed_seconds: float) -> None:
        """Check maximum workflow duration."""
        if elapsed_seconds > self.policy.max_workflow_duration_seconds:
            raise OrchestrationSecurityError(f"Duration limit exceeded: {elapsed_seconds:.1f}s > {self.policy.max_workflow_duration_seconds}s")

    def sanitize_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Scan and redact any credentials/secrets from workflow metadata."""
        sanitized = {}
        for k, v in data.items():
            if isinstance(v, str):
                has_secret, secrets = SecretDetector.contains_secret(v)
                if has_secret:
                    sanitized[k] = SecretDetector.sanitize_text(v)
                else:
                    sanitized[k] = v
            else:
                sanitized[k] = v
        return sanitized
