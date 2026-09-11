import pytest
from app.integrations.email.adapter import EmailAdapter


@pytest.mark.asyncio
async def test_email_adapter_operations():
    adapter = EmailAdapter()
    msgs = await adapter.execute("search_messages", {"query": "Phase 11"})
    assert len(msgs) > 0
    assert msgs[0]["subject"] == "ULTRON Phase 11 Report"
