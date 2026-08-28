import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.autonomy.contracts import AutonomyEventPayload, PriorityLevel
from app.autonomy.deduplication import DeduplicationManager
from app.autonomy.priority_engine import PriorityEngine
from app.database.repositories.autonomy_repo import AutonomyRepository

logger = logging.getLogger("ULTRON.EventBus")


class EventBus:
    """Internal Event Bus pipeline normalizing, deduplicating, prioritizing, and persisting events."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AutonomyRepository(db)

    async def publish_event(
        self,
        user_id: str,
        event_type: str,
        source: str,
        payload: Dict[str, Any],
        rule_id: Optional[str] = None,
        importance: str = "MEDIUM"
    ) -> Optional[AutonomyEventPayload]:
        # 1. Normalize & Deduplicate
        raw_str = f"{payload.get('url', payload.get('raw_content', ''))}"
        dedup_key = DeduplicationManager.generate_key(user_id, event_type, source, raw_str)

        if DeduplicationManager.is_duplicate(dedup_key):
            return None

        # 2. Prioritize
        priority = PriorityEngine.evaluate_priority(event_type, importance)

        # 3. Persist Event
        evt_model = await self.repo.create_event(
            user_id=user_id,
            rule_id=rule_id,
            event_type=event_type,
            source=source,
            deduplication_key=dedup_key,
            payload=payload,
            importance=priority.value
        )

        return AutonomyEventPayload(
            event_id=evt_model.id,
            user_id=user_id,
            event_type=event_type,
            source=source,
            deduplication_key=dedup_key,
            payload=payload,
            importance=priority,
            timestamp=evt_model.created_at.isoformat()
        )
