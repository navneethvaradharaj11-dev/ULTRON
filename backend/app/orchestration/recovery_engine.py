import logging
from typing import Dict, Any, Optional
from app.orchestration.failure_manager import FailureManager

logger = logging.getLogger(__name__)

class RecoveryEngine:
    """Recovery Engine implementing bounded automatic recovery strategies."""

    @classmethod
    def determine_recovery_action(
        cls,
        failure_type: str,
        task_id: str,
        agent: str,
        retry_count: int,
        max_retries: int = 3,
        error_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Determine appropriate recovery action based on failure type."""

        if failure_type == "SECURITY_FAILURE":
            return {
                "action": "STOP",
                "reason": "Security violation cannot be automatically recovered"
            }

        if failure_type == "APPROVAL_REQUIRED":
            return {
                "action": "WAIT_APPROVAL",
                "reason": "Operation requires human approval"
            }

        if retry_count >= max_retries:
            return {
                "action": "REPLAN_OR_FAIL",
                "reason": f"Maximum retries ({max_retries}) reached for task '{task_id}'"
            }

        if failure_type in ("TRANSIENT", "TIMEOUT"):
            return {
                "action": "RETRY_TASK",
                "target_task_id": task_id,
                "strategy": "exponential_backoff",
                "new_retry_count": retry_count + 1
            }

        if failure_type == "VALIDATION_FAILURE" and agent in ("coder", "code_agent"):
            return {
                "action": "FEEDBACK_RETRY",
                "target_task_id": task_id,
                "target_agent": "coder",
                "feedback": error_context.get("error_message") if error_context else "Compilation or test failed",
                "new_retry_count": retry_count + 1
            }

        if failure_type == "AGENT_FAILURE":
            # Fallback to general commander or alternative agent
            alt_agent = "commander" if agent != "commander" else "planner"
            return {
                "action": "ALTERNATIVE_AGENT",
                "target_task_id": task_id,
                "alternative_agent": alt_agent,
                "new_retry_count": retry_count + 1
            }

        return {
            "action": "RETRY_TASK",
            "target_task_id": task_id,
            "new_retry_count": retry_count + 1
        }
