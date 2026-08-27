import time
import inspect
import asyncio
import logging
from typing import Dict, Any, Callable, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.tools.calculator import safe_calculator
from app.tools.filesystem import filesystem_read, filesystem_write
from app.tools.web_search import web_search_tool
from app.tools.datetime_tool import get_current_datetime
from app.security.permissions import PermissionManager
from app.security.audit import AuditLogger

logger = logging.getLogger("ULTRON.ToolRegistry")


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        func: Callable,
        requires_approval: bool = False
    ):
        self.name = name
        self.description = description
        self.parameters_schema = parameters_schema
        self.func = func
        self.requires_approval = requires_approval


class ToolRegistry:
    """Central registry storing and executing safe ULTRON tools."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool
        logger.info("Registered tool: '%s'", tool.name)

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters_schema": t.parameters_schema,
                "requires_approval": t.requires_approval
            }
            for t in self._tools.values()
        ]

    async def execute_tool(
        self,
        name: str,
        params: Dict[str, Any],
        user_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """Execute a tool with timeout control, permission checks, and audit logging."""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found", "success": False}

        start_time = time.time()

        # Check permissions if database session provided
        requires_approval = tool.requires_approval
        if db and user_id:
            perm_manager = PermissionManager(db)
            perm = await perm_manager.get_permission(user_id, name)
            if perm == "deny":
                return {"error": f"Execution of tool '{name}' denied by security policy", "success": False}
            elif perm == "require_approval":
                requires_approval = True

        if requires_approval:
            return {
                "requires_approval": True,
                "approval_status": "pending_approval",
                "tool_name": name,
                "params": params,
                "message": f"Tool '{name}' requires explicit user approval before execution."
            }

        try:
            # Run tool function with timeout wrapper
            if inspect.iscoroutinefunction(tool.func):
                result = await asyncio.wait_for(tool.func(**params), timeout=settings.TOOL_TIMEOUT)
            else:
                loop = asyncio.get_running_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: tool.func(**params)),
                    timeout=settings.TOOL_TIMEOUT
                )

            exec_time_ms = int((time.time() - start_time) * 1000)

            if db and user_id:
                audit = AuditLogger(db)
                await audit.log_action(
                    action="execute_tool",
                    resource_type="tool",
                    user_id=user_id,
                    resource_id=name,
                    details={"params": params, "execution_time_ms": exec_time_ms, "status": "success"}
                )

            return {
                "success": True,
                "result": result,
                "execution_time_ms": exec_time_ms,
                "requires_approval": False
            }
        except asyncio.TimeoutError:
            exec_time_ms = int((time.time() - start_time) * 1000)
            logger.error("Tool '%s' execution timed out after %s seconds", name, settings.TOOL_TIMEOUT)
            return {
                "success": False,
                "error": f"Tool execution timed out after {settings.TOOL_TIMEOUT} seconds",
                "execution_time_ms": exec_time_ms
            }
        except Exception as e:
            exec_time_ms = int((time.time() - start_time) * 1000)
            logger.error("Tool execution failed (%s): %s", name, e)
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": exec_time_ms
            }

    def _register_default_tools(self):
        self.register(ToolDefinition(
            name="calculator",
            description="Evaluates mathematical expressions safely (e.g. '42 * 12 + sqrt(16)').",
            parameters_schema={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
            func=safe_calculator
        ))
        self.register(ToolDefinition(
            name="filesystem_read",
            description="Reads text content from a sandboxed file path.",
            parameters_schema={"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]},
            func=filesystem_read
        ))
        self.register(ToolDefinition(
            name="filesystem_write",
            description="Writes text content to a sandboxed file path.",
            parameters_schema={"type": "object", "properties": {"file_path": {"type": "string"}, "content": {"type": "string"}}, "required": ["file_path", "content"]},
            func=filesystem_write,
            requires_approval=True
        ))
        self.register(ToolDefinition(
            name="web_search",
            description="Searches the web for latest information.",
            parameters_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            func=web_search_tool
        ))
        self.register(ToolDefinition(
            name="get_current_datetime",
            description="Gets the current system UTC date and time.",
            parameters_schema={"type": "object", "properties": {}},
            func=get_current_datetime
        ))


default_tool_registry = ToolRegistry()
