import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.browser_session import BrowserSession

logger = logging.getLogger("ULTRON.BrowserManager")


class BrowserManager:
    """Manager responsible for Playwright Chromium session isolation, multi-tenant access control, and database sync."""

    def __init__(self):
        self._active_sessions: Dict[str, BrowserSession] = {}

    async def create_browser_session_async(
        self,
        user_id: str,
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> BrowserSession:
        """Create a new Playwright Chromium browser session with an isolated BrowserContext."""
        session = BrowserSession(
            user_id=user_id,
            execution_id=execution_id,
            session_id=session_id
        )
        self._active_sessions[session.session_id] = session

        logger.info(
            "Created Playwright browser session '%s' (user: %s, execution: %s)",
            session.session_id, user_id, execution_id
        )
        return session

    def create_browser_session(
        self,
        user_id: str,
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> BrowserSession:
        """Sync create_browser_session wrapper."""
        session = BrowserSession(user_id=user_id, execution_id=execution_id, session_id=session_id)
        self._active_sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str, user_id: str) -> Tuple[Optional[BrowserSession], Optional[str]]:
        """Retrieve active session enforcing multi-tenant ownership access control."""
        session = self._active_sessions.get(session_id)
        if not session:
            return None, f"Browser session '{session_id}' not found or has been closed."

        if not session.check_ownership(user_id):
            logger.warning("Unauthorized browser session access attempt! User '%s' requested session '%s' owned by '%s'.",
                           user_id, session_id, session.user_id)
            return None, "ACCESS_DENIED: You do not have authorization to access another user's browser session."

        return session, None

    async def close_browser_session_async(self, session_id: str, user_id: str) -> Tuple[bool, str]:
        """Close browser session and destroy Playwright context."""
        session, err = self.get_session(session_id, user_id)
        if err or not session:
            return False, err or "Session not found."

        await session.close_async()
        self._active_sessions.pop(session_id, None)
        logger.info("Closed Playwright browser session '%s'", session_id)
        return True, f"Session '{session_id}' successfully closed."

    def close_browser_session(self, session_id: str, user_id: str) -> Tuple[bool, str]:
        """Sync wrapper for close_browser_session."""
        session, err = self.get_session(session_id, user_id)
        if err or not session:
            return False, err or "Session not found."

        session.close()
        self._active_sessions.pop(session_id, None)
        return True, f"Session '{session_id}' successfully closed."

    def list_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """List active sessions for a specific user."""
        res = []
        for s in self._active_sessions.values():
            if s.user_id == user_id and s.status == "ACTIVE":
                res.append({
                    "session_id": s.session_id,
                    "user_id": s.user_id,
                    "execution_id": s.execution_id,
                    "current_url": s.current_url,
                    "step_count": s.step_count,
                    "status": s.status,
                    "created_at": s.created_at.isoformat(),
                    "has_playwright_runtime": s.playwright_page is not None
                })
        return res

    async def shutdown(self):
        """Close all sessions and cleanup Playwright Chromium instances."""
        for session in list(self._active_sessions.values()):
            await session.close_async()
        self._active_sessions.clear()


browser_manager = BrowserManager()
