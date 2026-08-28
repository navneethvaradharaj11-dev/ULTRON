import uuid
import logging
from typing import Dict, Optional, List
from app.computer.computer_session import ComputerSession
from app.computer.action_executor import ActionExecutor

logger = logging.getLogger("ULTRON.ComputerManager")


class ComputerManager:
    """Session lifecycle manager enforcing tenancy checks and fail-closed safety."""

    def __init__(self):
        self._sessions: Dict[str, ComputerSession] = {}
        self.action_executor = ActionExecutor()

    def create_session(
        self,
        user_id: str,
        execution_id: str,
        viewport_width: int = 1280,
        viewport_height: int = 800
    ) -> ComputerSession:
        session_id = str(uuid.uuid4())
        session = ComputerSession(session_id, user_id, execution_id, viewport_width, viewport_height)
        self._sessions[session_id] = session
        logger.info(f"Created active computer session '{session_id}' for user '{user_id}'")
        return session

    def get_session(self, session_id: str, user_id: Optional[str] = None) -> Optional[ComputerSession]:
        session = self._sessions.get(session_id)
        if session:
            if user_id and session.user_id != user_id:
                logger.warning(f"User '{user_id}' unauthorized access attempt to session '{session_id}' owned by '{session.user_id}'")
                return None
            return session
        return None

    def close_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        session = self.get_session(session_id, user_id)
        if session:
            session.close()
            return True
        return False

    def list_active_sessions(self, user_id: str) -> List[ComputerSession]:
        return [s for s in self._sessions.values() if s.user_id == user_id and s.is_active()]


# Global singleton instance
computer_manager = ComputerManager()
