import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.integrations.contracts import IntegrationDescriptor, OperationDescriptor
from app.integrations.integration_registry import integration_registry
from app.integrations.calendar.client import CalendarClient

logger = logging.getLogger("ULTRON.Integrations.CalendarAdapter")


class CalendarAdapter:
    """Calendar Service Adapter wrapping calendar operations with policy metadata."""

    INTEGRATION_ID = "calendar"

    def __init__(self, client: Optional[CalendarClient] = None):
        self.client = client or CalendarClient()
        self._register_descriptor()

    def _register_descriptor(self):
        desc = IntegrationDescriptor(
            id=self.INTEGRATION_ID,
            name="Calendar",
            version="1.0.0",
            provider="Calendar",
            description="Provider-Neutral Calendar Scheduling Integration",
            capabilities=["autonomy", "workflows"],
            risk_level="MEDIUM",
            authentication_type="OAUTH2",
            required_scopes=["READ_EVENTS", "CREATE_EVENT", "UPDATE_EVENT", "DELETE_EVENT"],
            supported_operations={
                "list_events": OperationDescriptor(
                    operation_id="list_events",
                    description="List upcoming calendar events",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["READ_EVENTS"]
                ),
                "create_event": OperationDescriptor(
                    operation_id="create_event",
                    description="Schedule a new calendar event",
                    risk_level="MEDIUM",
                    requires_approval=False,
                    required_scopes=["CREATE_EVENT"]
                ),
                "cancel_event": OperationDescriptor(
                    operation_id="cancel_event",
                    description="Cancel or delete a calendar event",
                    risk_level="HIGH",
                    requires_approval=True,
                    required_scopes=["DELETE_EVENT"]
                )
            }
        )
        integration_registry.register(desc)

    async def execute(self, operation_id: str, parameters: Dict[str, Any]) -> Any:
        op = operation_id.lower()
        if op == "list_events":
            return await self.client.list_events()
        elif op == "create_event":
            now = datetime.utcnow()
            start_t = parameters.get("start_time", now.isoformat())
            end_t = parameters.get("end_time", (now + timedelta(hours=1)).isoformat())
            return await self.client.create_event(parameters.get("title", "New Event"), start_t, end_t, parameters.get("description"))
        elif op == "cancel_event":
            return await self.client.cancel_event(parameters.get("event_id", "evt_1"))
        else:
            raise ValueError(f"Unsupported Calendar operation '{op}'")
