import logging
from typing import Dict, Any, List, Optional
from app.ai.model_manager import ModelManager
from app.perception.perception_engine import PerceptionEngine
from app.computer.computer_manager import computer_manager

logger = logging.getLogger("ULTRON.ComputerAgent")


class ComputerAgent:
    """Specialist perception-enabled agent for controlled computer and visual interaction."""

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()
        self.perception_engine = PerceptionEngine()

    async def execute(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default_user",
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute task using OBSERVE -> PERCEIVE -> GROUND -> ACT -> VERIFY -> RECOVER loop."""
        logger.info("ComputerAgent executing goal: '%s'", goal)
        context = context or {}
        exec_id = execution_id or "default_exec"

        sess_id = session_id or context.get("computer_session_id")
        if not sess_id:
            sess = computer_manager.create_session(user_id, exec_id)
            sess_id = sess.session_id

        # 1. OBSERVE & PERCEIVE
        dom_elements = context.get("dom_elements")
        perception_data = await self.perception_engine.perceive_state(
            session_id=sess_id,
            execution_id=exec_id,
            dom_elements=dom_elements
        )

        # 2. GROUND TARGET
        grounding = self.perception_engine.ground_instruction(goal, perception_data)
        if not grounding:
            logger.warning("ComputerAgent could not ground goal: '%s'", goal)
            return {
                "status": "FAILED",
                "agent_name": "computer",
                "output": "TARGET_NOT_FOUND: Could not ground instruction to visual UI target.",
                "confidence": 0.0,
                "perception": perception_data
            }

        # 3. SAFETY CHECK & ACT
        goal_low = goal.lower()
        action_type = "CLICK" if "click" in goal_low else ("TYPE" if "type" in goal_low or "search" in goal_low else "MOVE")
        params = {"x": grounding.bounding_box.x, "y": grounding.bounding_box.y}
        if action_type == "TYPE":
            params["text"] = context.get("input_text", "Python IDEs")

        sess = computer_manager.get_session(sess_id, user_id)
        if not sess:
            return {
                "status": "FAILED",
                "agent_name": "computer",
                "output": "COMPUTER_UNAVAILABLE: Active session invalid or closed.",
                "confidence": 0.0
            }

        action_result = await computer_manager.action_executor.execute_action(
            session=sess,
            action_type=action_type,
            target={"label": grounding.description, "x": grounding.bounding_box.x, "y": grounding.bounding_box.y},
            parameters=params,
            confidence=grounding.confidence
        )

        # 4. VERIFY & RECOVER
        if action_result.get("approval_state") == "REQUIRES_APPROVAL" or action_result.get("status") == "PENDING_APPROVAL":
            return {
                "status": "REQUIRES_APPROVAL",
                "agent_name": "computer",
                "output": f"Action '{action_type}' requires backend user approval: {action_result.get('reason', 'Sensitive target action requiring approval')}",
                "confidence": grounding.confidence,
                "action_result": action_result,
                "session_id": sess_id
            }

        elif action_result.get("status") == "COMPLETED":
            return {
                "status": "COMPLETED",
                "agent_name": "computer",
                "output": f"Successfully performed {action_type} on '{grounding.description}' at ({grounding.bounding_box.x}, {grounding.bounding_box.y}).",
                "confidence": grounding.confidence,
                "action_result": action_result,
                "perception": perception_data,
                "session_id": sess_id
            }

        else:
            logger.info("Action failed (%s). Attempting recovery...", action_result.get("error"))
            return {
                "status": "FAILED",
                "agent_name": "computer",
                "output": f"ACTION_FAILED: {action_result.get('error')}",
                "confidence": grounding.confidence,
                "action_result": action_result,
                "session_id": sess_id
            }

    async def execute_task(
        self,
        task_id: str,
        goal: str,
        context: Dict[str, Any],
        user_id: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """Alias for execute to fit task engine invocation."""
        return await self.execute(goal, context, user_id, execution_id)
