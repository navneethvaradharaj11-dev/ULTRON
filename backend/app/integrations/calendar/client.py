import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.integrations.calendar.models import CalendarEventModel

logger = logging.getLogger("ULTRON.Integrations.CalendarClient")


class CalendarClient:
    """Mock/Real provider-neutral calendar client."""

    async def list_events(self) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        evt = CalendarEventModel(
            id="evt_1",
            title="ULTRON System Architecture Review",
            description="Review Phase 11 Integration Architecture",
            start_time=now.isoformat(),
            end_time=(now + timedelta(hours=1)).isoformat(),
            location="Virtual / Zoom",
            attendees=["user@ultron.ai"]
        )
        return [evt.model_dump() if hasattr(evt, "model_dump") else evt.dict()]

    async def create_event(self, title: str, start_time: str, end_time: str, description: Optional[str] = None) -> Dict[str, Any]:
        _evt = CalendarEventModel(
            id="evt_2",
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        return _evt.model_dump() if hasattr(_evt, "model_dump") else _evt.dict()

    async def cancel_event(self, event_id: str) -> Dict[str, Any]:
        return {"cancelled": True, "event_id": event_id, "status": "cancelled"}
