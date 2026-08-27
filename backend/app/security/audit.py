import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import AuditLog

logger = logging.getLogger("ULTRON.Audit")


class AuditLogger:
    """Logs security and sensitive system actions into audit_logs table."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_action(
        self,
        action: str,
        resource_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details,
            ip_address=ip_address
        )
        self.db.add(audit_entry)
        await self.db.commit()
        await self.db.refresh(audit_entry)
        logger.info("AUDIT: user=%s action=%s target=%s:%s", user_id, action, resource_type, resource_id)
        return audit_entry
