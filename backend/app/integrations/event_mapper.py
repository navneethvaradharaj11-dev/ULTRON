import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from app.autonomy.contracts import AutonomyEventPayload

logger = logging.getLogger("ULTRON.Integrations.EventMapper")


class EventMapper:
    """Normalizes external integration webhooks into structured Phase 9 AutonomyEventPayload models."""

    @staticmethod
    def map_to_autonomy_event(
        provider: str,
        event_type: str,
        user_id: str,
        payload_json: Dict[str, Any]
    ) -> AutonomyEventPayload:
        normalized_name = f"{provider.lower()}.{event_type.lower()}"
        return AutonomyEventPayload(
            event_id=str(uuid.uuid4()),
            user_id=user_id,
            event_type=normalized_name,
            source=provider.lower(),
            deduplication_key=f"{provider.lower()}:{event_type}:{user_id}",
            payload=payload_json,
            timestamp=datetime.utcnow().isoformat()
        )

