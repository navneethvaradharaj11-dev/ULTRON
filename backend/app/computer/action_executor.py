import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.computer.computer_session import ComputerSession
from app.computer.input_controller import InputController
from app.computer.computer_policy import ComputerPolicy

logger = logging.getLogger("ULTRON.ActionExecutor")


class ActionExecutor:
    """Dispatches and verifies controlled computer actions."""

    def __init__(self):
        self.input_controller = InputController()
        self.policy = ComputerPolicy()

    async def execute_action(
        self,
        session: ComputerSession,
        action_type: str,
        target: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        target = target or {}
        parameters = parameters or {}
        action_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Policy validation
        approval_state, reason = self.policy.evaluate_action_risk(
            action_type=action_type,
            target=target,
            parameters=parameters,
            confidence=confidence,
            viewport_width=session.viewport_width,
            viewport_height=session.viewport_height
        )

        if approval_state == "FORBIDDEN":
            logger.warning(f"Action '{action_type}' denied by policy: {reason}")
            return {
                "action_id": action_id,
                "session_id": session.session_id,
                "action_type": action_type,
                "status": "FAILED",
                "approval_state": "FORBIDDEN",
                "error": reason,
                "confidence": confidence,
                "timestamp": timestamp
            }

        if approval_state == "REQUIRES_APPROVAL":
            logger.info(f"Action '{action_type}' requires backend approval: {reason}")
            return {
                "action_id": action_id,
                "session_id": session.session_id,
                "action_type": action_type,
                "status": "PENDING_APPROVAL",
                "approval_state": "REQUIRES_APPROVAL",
                "reason": reason,
                "confidence": confidence,
                "timestamp": timestamp
            }

        # Execute input action
        try:
            res = await self.input_controller.execute_input_action(session, action_type, parameters)
            return {
                "action_id": action_id,
                "session_id": session.session_id,
                "action_type": action_type,
                "status": "COMPLETED",
                "approval_state": "AUTO_APPROVED",
                "result": res,
                "confidence": confidence,
                "timestamp": timestamp
            }
        except Exception as e:
            logger.error(f"Action '{action_type}' execution error: {e}")
            return {
                "action_id": action_id,
                "session_id": session.session_id,
                "action_type": action_type,
                "status": "FAILED",
                "approval_state": "AUTO_APPROVED",
                "error": str(e),
                "confidence": confidence,
                "timestamp": timestamp
            }
