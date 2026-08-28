import logging
from typing import Dict, Any, List
from app.computer.computer_session import ComputerSession

logger = logging.getLogger("ULTRON.KeyboardController")


class KeyboardController:
    """Performs controlled keyboard interactions."""

    async def type_text(self, session: ComputerSession, text: str) -> Dict[str, Any]:
        if len(text) > 1000:
            text = text[:1000]

        logger.info(f"Keyboard TYPE text length={len(text)} in session '{session.session_id}'")
        return {"action": "TYPE", "text_length": len(text), "status": "COMPLETED"}

    async def press_key(self, session: ComputerSession, key: str) -> Dict[str, Any]:
        logger.info(f"Keyboard PRESS_KEY '{key}' in session '{session.session_id}'")
        return {"action": "PRESS_KEY", "key": key, "status": "COMPLETED"}

    async def hotkey(self, session: ComputerSession, keys: List[str]) -> Dict[str, Any]:
        logger.info(f"Keyboard HOTKEY combination {keys} in session '{session.session_id}'")
        return {"action": "HOTKEY", "keys": keys, "status": "COMPLETED"}
