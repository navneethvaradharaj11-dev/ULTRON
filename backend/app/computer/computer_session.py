import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("ULTRON.ComputerSession")


class ComputerSession:
    """Manages active controlled computer interaction session state and bounds."""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        execution_id: str,
        viewport_width: int = 1280,
        viewport_height: int = 800
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.execution_id = execution_id
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.status = "ACTIVE"
        self.created_at = datetime.utcnow()
        self.closed_at: Optional[datetime] = None
        self.action_count = 0

    def close(self):
        self.status = "CLOSED"
        self.closed_at = datetime.utcnow()
        logger.info(f"Closed computer session '{self.session_id}'")

    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x <= self.viewport_width and 0 <= y <= self.viewport_height
