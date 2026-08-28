import logging
from typing import Dict, Any

logger = logging.getLogger("ULTRON.ResourceBudget")


class ResourceBudgetExceededError(Exception):
    """Exception raised when workflow resource limits are exceeded."""
    pass


class ResourceBudgetTracker:
    """Enforces execution resource bounds (max tool calls, browser steps, runtime seconds)."""

    def __init__(
        self,
        max_tool_calls: int = 50,
        max_runtime_seconds: int = 600,
        max_browser_steps: int = 20
    ):
        self.max_tool_calls = max_tool_calls
        self.max_runtime_seconds = max_runtime_seconds
        self.max_browser_steps = max_browser_steps

        self.used_tool_calls = 0
        self.used_runtime_seconds = 0
        self.used_browser_steps = 0

    def record_tool_call(self) -> None:
        self.used_tool_calls += 1
        if self.used_tool_calls > self.max_tool_calls:
            raise ResourceBudgetExceededError(f"RESOURCE_BUDGET_EXCEEDED: Max tool calls limit ({self.max_tool_calls}) reached.")

    def record_browser_step(self) -> None:
        self.used_browser_steps += 1
        if self.used_browser_steps > self.max_browser_steps:
            raise ResourceBudgetExceededError(f"RESOURCE_BUDGET_EXCEEDED: Max browser steps limit ({self.max_browser_steps}) reached.")
