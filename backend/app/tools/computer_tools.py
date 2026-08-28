import logging
from typing import Dict, Any, Optional, List
from app.computer.computer_manager import computer_manager
from app.security.computer_security import ComputerSecurityValidator

logger = logging.getLogger("ULTRON.ComputerTools")
validator = ComputerSecurityValidator()


async def computer_create_session(user_id: str, execution_id: str, viewport_width: int = 1280, viewport_height: int = 800) -> Dict[str, Any]:
    sess = computer_manager.create_session(user_id, execution_id, viewport_width, viewport_height)
    return {
        "status": "success",
        "session_id": sess.session_id,
        "viewport": {"width": sess.viewport_width, "height": sess.viewport_height}
    }


async def computer_execute_action(
    session_id: str,
    user_id: str,
    action_type: str,
    target: Optional[Dict[str, Any]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0
) -> Dict[str, Any]:
    sess = computer_manager.get_session(session_id, user_id)
    is_valid, msg = validator.validate_session_access(sess, user_id)
    if not is_valid:
        return {"status": "failed", "error": msg}

    target = target or {}
    parameters = parameters or {}

    allowed, approval_state, reason = validator.validate_action_safety(sess, action_type, target, parameters, confidence)
    if not allowed:
        return {"status": "failed", "error": reason, "approval_state": approval_state}

    res = await computer_manager.action_executor.execute_action(sess, action_type, target, parameters, confidence)
    return res


async def computer_close_session(session_id: str, user_id: str) -> Dict[str, Any]:
    success = computer_manager.close_session(session_id, user_id)
    return {"status": "success" if success else "failed"}
