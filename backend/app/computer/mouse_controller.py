import logging
from typing import Dict, Any, Optional
from app.computer.computer_session import ComputerSession

logger = logging.getLogger("ULTRON.MouseController")


class MouseController:
    """Performs controlled mouse interactions within viewport boundaries."""

    async def move(self, session: ComputerSession, x: int, y: int) -> Dict[str, Any]:
        if not session.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) outside viewport bounds ({session.viewport_width}x{session.viewport_height})")

        logger.info(f"Mouse MOVE to ({x}, {y}) in session '{session.session_id}'")
        return {"action": "MOVE", "x": x, "y": y, "status": "COMPLETED"}

    async def click(self, session: ComputerSession, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        if not session.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) outside viewport bounds ({session.viewport_width}x{session.viewport_height})")

        logger.info(f"Mouse CLICK ({button}) at ({x}, {y}) in session '{session.session_id}'")
        return {"action": "CLICK", "button": button, "x": x, "y": y, "status": "COMPLETED"}

    async def double_click(self, session: ComputerSession, x: int, y: int) -> Dict[str, Any]:
        if not session.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) outside viewport bounds ({session.viewport_width}x{session.viewport_height})")

        logger.info(f"Mouse DOUBLE_CLICK at ({x}, {y}) in session '{session.session_id}'")
        return {"action": "DOUBLE_CLICK", "x": x, "y": y, "status": "COMPLETED"}

    async def right_click(self, session: ComputerSession, x: int, y: int) -> Dict[str, Any]:
        if not session.is_within_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) outside viewport bounds ({session.viewport_width}x{session.viewport_height})")

        logger.info(f"Mouse RIGHT_CLICK at ({x}, {y}) in session '{session.session_id}'")
        return {"action": "RIGHT_CLICK", "x": x, "y": y, "status": "COMPLETED"}

    async def scroll(self, session: ComputerSession, delta_x: int, delta_y: int) -> Dict[str, Any]:
        logger.info(f"Mouse SCROLL ({delta_x}, {delta_y}) in session '{session.session_id}'")
        return {"action": "SCROLL", "delta_x": delta_x, "delta_y": delta_y, "status": "COMPLETED"}

    async def drag(self, session: ComputerSession, start_x: int, start_y: int, end_x: int, end_y: int) -> Dict[str, Any]:
        if not session.is_within_bounds(start_x, start_y) or not session.is_within_bounds(end_x, end_y):
            raise ValueError("Drag coordinates outside viewport bounds")

        logger.info(f"Mouse DRAG from ({start_x}, {start_y}) to ({end_x}, {end_y}) in session '{session.session_id}'")
        return {"action": "DRAG", "start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y, "status": "COMPLETED"}
