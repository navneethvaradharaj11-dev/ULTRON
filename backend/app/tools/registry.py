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
from app.tools import browser as browser_tools
from app.tools import code_tools
from app.tools import computer_tools
from app.tools import perception_tools
from app.tools.desktop_app import launch_desktop_app
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
        self.register(ToolDefinition(
            name="launch_desktop_app",
            description="Launches a native Windows desktop application and brings it to the foreground (e.g. WhatsApp, Spotify, Notepad, Calculator, Chrome, VS Code).",
            parameters_schema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "The name of the application to launch (e.g. 'whatsapp', 'spotify', 'notepad')"},
                    "target": {"type": "string", "description": "Optional file path, contact, or argument to open with the app"}
                },
                "required": ["app_name"]
            },
            func=launch_desktop_app
        ))

        # Phase 3 Browser Tools
        self.register(ToolDefinition(
            name="browser_navigate",
            description="Navigates to an approved URL in a browser session.",
            parameters_schema={"type": "object", "properties": {"url": {"type": "string"}, "session_id": {"type": "string"}}, "required": ["url"]},
            func=browser_tools.browser_navigate
        ))
        self.register(ToolDefinition(
            name="browser_back",
            description="Navigates back in browser history.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            func=browser_tools.browser_back
        ))
        self.register(ToolDefinition(
            name="browser_forward",
            description="Navigates forward in browser history.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            func=browser_tools.browser_forward
        ))
        self.register(ToolDefinition(
            name="browser_reload",
            description="Reloads the active browser page.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            func=browser_tools.browser_reload
        ))
        self.register(ToolDefinition(
            name="browser_read_page",
            description="Inspects current page content with prompt injection defense.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            func=browser_tools.browser_read_page
        ))
        self.register(ToolDefinition(
            name="browser_find_element",
            description="Identifies elements on the active page by text, role, or ID.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "query": {"type": "string"}, "element_type": {"type": "string"}}, "required": ["session_id", "query"]},
            func=browser_tools.browser_find_element
        ))
        self.register(ToolDefinition(
            name="browser_click",
            description="Clicks a target element on the browser page.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "element_query": {"type": "string"}}, "required": ["session_id", "element_query"]},
            func=browser_tools.browser_click
        ))
        self.register(ToolDefinition(
            name="browser_type",
            description="Enters text into an input field on the page.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "element_query": {"type": "string"}, "text": {"type": "string"}}, "required": ["session_id", "element_query", "text"]},
            func=browser_tools.browser_type
        ))
        self.register(ToolDefinition(
            name="browser_select",
            description="Selects an option in a dropdown element.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "element_query": {"type": "string"}, "value": {"type": "string"}}, "required": ["session_id", "element_query", "value"]},
            func=browser_tools.browser_select
        ))
        self.register(ToolDefinition(
            name="browser_extract",
            description="Extracts structured facts and evidence from page observations.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "facts": {"type": "array"}}, "required": ["session_id", "facts"]},
            func=browser_tools.browser_extract
        ))
        self.register(ToolDefinition(
            name="browser_screenshot",
            description="Captures a preview image of the browser page.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}}, "required": ["session_id"]},
            func=browser_tools.browser_screenshot
        ))

        # Phase 4 Code Tools
        from app.tools import code_tools
        self.register(ToolDefinition(
            name="code_create_file",
            description="Creates a file inside the isolated code sandbox workspace.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path"]},
            func=code_tools.code_create_file
        ))
        self.register(ToolDefinition(
            name="code_read_file",
            description="Reads a file from the isolated code sandbox workspace.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "path": {"type": "string"}}, "required": ["path"]},
            func=code_tools.code_read_file
        ))
        self.register(ToolDefinition(
            name="code_update_file",
            description="Updates a file inside the isolated code sandbox workspace.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path"]},
            func=code_tools.code_update_file
        ))
        self.register(ToolDefinition(
            name="code_delete_file",
            description="Deletes a file from the isolated code sandbox workspace.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "path": {"type": "string"}}, "required": ["path"]},
            func=code_tools.code_delete_file
        ))
        self.register(ToolDefinition(
            name="code_list_files",
            description="Lists all files in the code sandbox workspace.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}}, "required": []},
            func=code_tools.code_list_files
        ))
        self.register(ToolDefinition(
            name="code_compile",
            description="Compiles C, C++, or other compiled code inside the isolated sandbox.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "language": {"type": "string"}, "entrypoint": {"type": "string"}}, "required": ["language", "entrypoint"]},
            func=code_tools.code_compile
        ))
        self.register(ToolDefinition(
            name="code_execute",
            description="Executes code (Python, JS, C, C++) inside the isolated sandbox.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "language": {"type": "string"}, "entrypoint": {"type": "string"}}, "required": ["language", "entrypoint"]},
            func=code_tools.code_execute
        ))
        self.register(ToolDefinition(
            name="code_test",
            description="Executes test suites inside the isolated code sandbox.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "language": {"type": "string"}, "test_file": {"type": "string"}}, "required": ["language", "test_file"]},
            func=code_tools.code_test
        ))
        self.register(ToolDefinition(
            name="code_get_output",
            description="Retrieves execution output files from the sandbox.",
            parameters_schema={"type": "object", "properties": {"execution_id": {"type": "string"}, "task_id": {"type": "string"}, "filename": {"type": "string"}}, "required": ["filename"]},
            func=code_tools.code_get_output
        ))

        # Phase 5: Controlled Computer Interaction & Perception Tools
        self.register(ToolDefinition(
            name="computer_create_session",
            description="Creates a new controlled computer interaction session.",
            parameters_schema={"type": "object", "properties": {"user_id": {"type": "string"}, "execution_id": {"type": "string"}, "viewport_width": {"type": "integer"}, "viewport_height": {"type": "integer"}}, "required": ["user_id", "execution_id"]},
            func=computer_tools.computer_create_session
        ))
        self.register(ToolDefinition(
            name="computer_execute_action",
            description="Executes a controlled computer action (MOVE, CLICK, TYPE, etc.).",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "user_id": {"type": "string"}, "action_type": {"type": "string"}, "target": {"type": "object"}, "parameters": {"type": "object"}, "confidence": {"type": "number"}}, "required": ["session_id", "user_id", "action_type"]},
            func=computer_tools.computer_execute_action
        ))
        self.register(ToolDefinition(
            name="computer_close_session",
            description="Closes an active computer interaction session.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "user_id": {"type": "string"}}, "required": ["session_id", "user_id"]},
            func=computer_tools.computer_close_session
        ))
        self.register(ToolDefinition(
            name="perception_perceive_state",
            description="Captures viewport state and runs multi-modal perception analysis.",
            parameters_schema={"type": "object", "properties": {"session_id": {"type": "string"}, "execution_id": {"type": "string"}, "dom_elements": {"type": "array"}}, "required": ["session_id", "execution_id"]},
            func=perception_tools.perception_perceive_state
        ))
        self.register(ToolDefinition(
            name="perception_ground_target",
            description="Grounds a natural language instruction to a visual UI target.",
            parameters_schema={"type": "object", "properties": {"instruction": {"type": "string"}, "perception_data": {"type": "object"}}, "required": ["instruction", "perception_data"]},
            func=perception_tools.perception_ground_target
        ))


default_tool_registry = ToolRegistry()


