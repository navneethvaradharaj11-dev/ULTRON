import pytest
from app.core.resource_budget import ResourceBudgetTracker, ResourceBudgetExceededError


def test_resource_budget_limits():
    budget = ResourceBudgetTracker(max_tool_calls=2)
    budget.record_tool_call()
    budget.record_tool_call()

    with pytest.raises(ResourceBudgetExceededError, match="RESOURCE_BUDGET_EXCEEDED"):
        budget.record_tool_call()
