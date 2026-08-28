import logging
from typing import Dict, Any, List, Optional
from app.config.settings import settings
from app.computer.computer_session import ComputerSession
from app.computer.mouse_controller import MouseController
from app.computer.keyboard_controller import KeyboardController

logger = logging.getLogger("ULTRON.InputController")


class InputController:
    """Combines mouse and keyboard operations while enforcing rate limits."""

    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    async def execute_input_action(
        self,
        session: ComputerSession,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Dispatch input action to mouse or keyboard controller with limit enforcement."""
        session.action_count += 1
        if session.action_count > settings.MAX_COMPUTER_ACTIONS:
            raise ValueError(f"Exceeded maximum computer actions limit ({settings.MAX_COMPUTER_ACTIONS})")

        act_upper = action_type.upper()

        if act_upper == "MOVE":
            return await self.mouse.move(session, parameters.get("x", 0), parameters.get("y", 0))
        elif act_upper == "CLICK":
            return await self.mouse.click(session, parameters.get("x", 0), parameters.get("y", 0), parameters.get("button", "left"))
        elif act_upper == "DOUBLE_CLICK":
            return await self.mouse.double_click(session, parameters.get("x", 0), parameters.get("y", 0))
        elif act_upper == "RIGHT_CLICK":
            return await self.mouse.right_click(session, parameters.get("x", 0), parameters.get("y", 0))
        elif act_upper == "SCROLL":
            return await self.mouse.scroll(session, parameters.get("delta_x", 0), parameters.get("delta_y", 0))
        elif act_upper == "DRAG":
            return await self.mouse.drag(session, parameters.get("start_x", 0), parameters.get("start_y", 0), parameters.get("end_x", 0), parameters.get("end_y", 0))
        elif act_upper == "TYPE":
            return await self.keyboard.type_text(session, parameters.get("text", ""))
        elif act_upper == "PRESS_KEY":
            return await self.keyboard.press_key(session, parameters.get("key", ""))
        elif act_upper == "HOTKEY":
            return await self.keyboard.hotkey(session, parameters.get("keys", []))
        elif act_upper == "WAIT":
            return {"action": "WAIT", "duration": parameters.get("duration", 1.0), "status": "COMPLETED"}
        else:
            raise ValueError(f"Unsupported computer input action: {action_type}")
