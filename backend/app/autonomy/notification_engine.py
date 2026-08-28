import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.intelligence.secret_detector import SecretDetector

logger = logging.getLogger("ULTRON.NotificationEngine")


class NotificationEngine:
    """Notification Engine preparing and dispatching user notifications without secret leakage."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AutonomyRepository(db)

    async def send_notification(
        self,
        user_id: str,
        title: str,
        summary: str,
        priority: str = "MEDIUM",
        rule_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        # Redact raw secrets before sending
        safe_title = SecretDetector.sanitize_text(title)
        safe_summary = SecretDetector.sanitize_text(summary)

        notif = await self.repo.create_notification(
            user_id=user_id,
            title=safe_title,
            summary=safe_summary,
            priority=priority,
            rule_id=rule_id,
            payload=payload or {}
        )

        logger.info("Notification dispatched to user '%s': [%s] %s", user_id, priority, safe_title)

        return {
            "notification_id": notif.id,
            "user_id": user_id,
            "title": safe_title,
            "summary": safe_summary,
            "priority": priority,
            "created_at": notif.created_at.isoformat()
        }
