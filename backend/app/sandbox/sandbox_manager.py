import logging
from typing import Dict, Optional
from app.sandbox.sandbox_session import SandboxSession
from app.sandbox.resource_limits import ResourceLimits
from app.sandbox.network_policy import NetworkPolicyMode

logger = logging.getLogger("ULTRON.SandboxManager")


class SandboxUnavailableError(Exception):
    """Raised when sandbox runtime environment is unavailable."""
    pass


class SandboxManager:
    """Orchestrator for managing sandbox sessions, lifecycle, isolation, and fail-closed safety."""

    def __init__(self):
        self._sessions: Dict[str, SandboxSession] = {}
        self._is_sandbox_healthy: bool = True  # Can be probed/configured

    def is_sandbox_available(self) -> bool:
        """Probe if sandbox environment is safe and available."""
        return self._is_sandbox_healthy

    def get_or_create_session(
        self,
        execution_id: str,
        task_id: str,
        user_id: str,
        limits: Optional[ResourceLimits] = None,
        network_mode: NetworkPolicyMode = NetworkPolicyMode.DENY_ALL
    ) -> SandboxSession:
        """Retrieve existing or spawn a new isolated sandbox session.
        FAILS CLOSED if sandbox environment is unavailable.
        """
        if not self.is_sandbox_available():
            raise SandboxUnavailableError("SANDBOX_UNAVAILABLE: Secure sandbox runtime environment is currently unavailable.")

        session_key = f"{execution_id}_{task_id}"
        if session_key in self._sessions and self._sessions[session_key].active:
            session = self._sessions[session_key]

            # Validate ownership
            if session.user_id != user_id:
                raise PermissionError(f"ACCESS_DENIED: User '{user_id}' does not own workspace session '{session_key}'.")
            return session

        session = SandboxSession(
            execution_id=execution_id,
            task_id=task_id,
            user_id=user_id,
            limits=limits,
            network_mode=network_mode
        )
        self._sessions[session_key] = session
        logger.info("Initialized sandbox session '%s' for user '%s'", session_key, user_id)
        return session

    def get_session(self, execution_id: str, task_id: str, user_id: str) -> Optional[SandboxSession]:
        session_key = f"{execution_id}_{task_id}"
        session = self._sessions.get(session_key)
        if session:
            if session.user_id != user_id:
                raise PermissionError(f"ACCESS_DENIED: User '{user_id}' does not own workspace session '{session_key}'.")
            return session
        return None

    def destroy_session(self, execution_id: str, task_id: str, user_id: Optional[str] = None):
        session_key = f"{execution_id}_{task_id}"
        session = self._sessions.pop(session_key, None)
        if session:
            if user_id and session.user_id != user_id:
                raise PermissionError(f"ACCESS_DENIED: User '{user_id}' cannot destroy session '{session_key}'.")
            session.close()
            logger.info("Destroyed sandbox session '%s'", session_key)

    def destroy_all(self):
        keys = list(self._sessions.keys())
        for k in keys:
            sess = self._sessions.pop(k, None)
            if sess:
                sess.close()
        logger.info("Destroyed all active sandbox sessions.")


default_sandbox_manager = SandboxManager()
