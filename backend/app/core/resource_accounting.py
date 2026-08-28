import logging
from typing import Dict, Any

logger = logging.getLogger("ULTRON.ResourceAccountingLayer")


class WorkflowResourceLimitExceeded(Exception):
    """Exception raised when workflow resource limits are exceeded."""
    pass


class ResourceAccountingLayer:
    """Unified resource accounting layer tracking model calls, tokens, tool calls, browser steps,
    computer actions, sandbox executions, and total runtime per workflow.
    """

    def __init__(
        self,
        workflow_id: str,
        max_model_calls: int = 50,
        max_tokens: int = 100000,
        max_tool_calls: int = 50,
        max_browser_actions: int = 20,
        max_computer_actions: int = 15,
        max_sandbox_executions: int = 10
    ):
        self.workflow_id = workflow_id
        self.max_model_calls = max_model_calls
        self.max_tokens = max_tokens
        self.max_tool_calls = max_tool_calls
        self.max_browser_actions = max_browser_actions
        self.max_computer_actions = max_computer_actions
        self.max_sandbox_executions = max_sandbox_executions

        self.used_model_calls = 0
        self.used_tokens = 0
        self.used_tool_calls = 0
        self.used_browser_actions = 0
        self.used_computer_actions = 0
        self.used_sandbox_executions = 0

    def record_model_call(self, token_count: int = 0) -> None:
        self.used_model_calls += 1
        self.used_tokens += token_count
        if self.used_model_calls > self.max_model_calls:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max model calls limit ({self.max_model_calls}) reached.")
        if self.used_tokens > self.max_tokens:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max token count limit ({self.max_tokens}) reached.")

    def record_tool_call(self) -> None:
        self.used_tool_calls += 1
        if self.used_tool_calls > self.max_tool_calls:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max tool calls limit ({self.max_tool_calls}) reached.")

    def record_browser_action(self) -> None:
        self.used_browser_actions += 1
        if self.used_browser_actions > self.max_browser_actions:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max browser actions limit ({self.max_browser_actions}) reached.")

    def record_computer_action(self) -> None:
        self.used_computer_actions += 1
        if self.used_computer_actions > self.max_computer_actions:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max computer actions limit ({self.max_computer_actions}) reached.")

    def record_sandbox_execution(self) -> None:
        self.used_sandbox_executions += 1
        if self.used_sandbox_executions > self.max_sandbox_executions:
            raise WorkflowResourceLimitExceeded(f"RESOURCE_EXCEEDED: Max sandbox executions limit ({self.max_sandbox_executions}) reached.")

    def get_summary(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "model_calls": f"{self.used_model_calls}/{self.max_model_calls}",
            "tokens": f"{self.used_tokens}/{self.max_tokens}",
            "tool_calls": f"{self.used_tool_calls}/{self.max_tool_calls}",
            "browser_actions": f"{self.used_browser_actions}/{self.max_browser_actions}",
            "computer_actions": f"{self.used_computer_actions}/{self.max_computer_actions}",
            "sandbox_executions": f"{self.used_sandbox_executions}/{self.max_sandbox_executions}"
        }
