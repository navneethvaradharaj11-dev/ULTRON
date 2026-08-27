import pytest
from app.tools.registry import default_tool_registry
from app.tools.calculator import safe_calculator
from app.tools.filesystem import filesystem_write, filesystem_read


def test_safe_calculator():
    res = safe_calculator("42 * 12 + 4")
    assert res == "508"

    with pytest.raises(ValueError):
        safe_calculator("import os; os.system('dir')")


def test_tool_registry_list():
    tools = default_tool_registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "filesystem_read" in tool_names
    assert "filesystem_write" in tool_names
    assert "web_search" in tool_names
    assert "get_current_datetime" in tool_names


@pytest.mark.asyncio
async def test_tool_execution():
    res = await default_tool_registry.execute_tool("calculator", {"expression": "10 + 25"})
    assert res["success"] is True
    assert res["result"] == "35"
