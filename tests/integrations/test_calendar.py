import pytest
from app.integrations.calendar.adapter import CalendarAdapter


@pytest.mark.asyncio
async def test_calendar_adapter_operations():
    adapter = CalendarAdapter()
    events = await adapter.execute("list_events", {})
    assert len(events) > 0
    assert "ULTRON" in events[0]["title"]
