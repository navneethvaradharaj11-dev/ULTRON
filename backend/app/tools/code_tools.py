import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.sandbox.sandbox_manager import default_sandbox_manager, SandboxUnavailableError
from app.sandbox.sandbox_policy import SandboxPolicy, SandboxActionRisk

logger = logging.getLogger("ULTRON.Tools.Code")


async def code_create_file(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Create a file inside the isolated code execution sandbox workspace."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    path = params.get("path")
    content = params.get("content", "")

    if not path:
        return {"success": False, "error": "Missing required parameter 'path'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        res = session.create_file(path, content)
        return {"success": True, "result": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_read_file(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Read a file from the code execution sandbox workspace."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    path = params.get("path")

    if not path:
        return {"success": False, "error": "Missing required parameter 'path'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        content = session.read_file(path)
        return {"success": True, "content": content, "path": path}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_update_file(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Update a file inside the code execution sandbox workspace."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    path = params.get("path")
    content = params.get("content", "")

    if not path:
        return {"success": False, "error": "Missing required parameter 'path'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        res = session.update_file(path, content)
        return {"success": True, "result": res}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_delete_file(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Delete a file from the code execution sandbox workspace."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    path = params.get("path")

    if not path:
        return {"success": False, "error": "Missing required parameter 'path'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        deleted = session.delete_file(path)
        return {"success": True, "deleted": deleted, "path": path}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_list_files(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """List all files in the code execution sandbox workspace."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        files = session.list_files()
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_compile(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Compile code inside the isolated code execution sandbox."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    language = params.get("language")
    entrypoint = params.get("entrypoint")

    if not language or not entrypoint:
        return {"success": False, "error": "Missing 'language' or 'entrypoint'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        res = session.compile_code(language, entrypoint)
        return {
            "success": res.status == "COMPLETED",
            "status": res.status,
            "exit_code": res.exit_code,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration_ms": res.duration_ms
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_execute(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Execute compiled/interpreted code inside the isolated sandbox."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    language = params.get("language")
    entrypoint = params.get("entrypoint")
    args = params.get("args")

    if not language or not entrypoint:
        return {"success": False, "error": "Missing 'language' or 'entrypoint'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        res = session.execute_code(language, entrypoint, args=args)
        return {
            "success": res.status == "COMPLETED",
            "status": res.status,
            "exit_code": res.exit_code,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration_ms": res.duration_ms
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_test(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Run tests for code inside the isolated sandbox."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    language = params.get("language")
    test_file = params.get("test_file")

    if not language or not test_file:
        return {"success": False, "error": "Missing 'language' or 'test_file'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        res = session.run_tests(language, test_file)
        return {
            "success": res.status == "COMPLETED",
            "status": res.status,
            "exit_code": res.exit_code,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "duration_ms": res.duration_ms
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def code_get_output(
    params: Dict[str, Any],
    user_id: str = "system",
    db: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """Retrieve output from sandbox output directory."""
    execution_id = params.get("execution_id", "default_exec")
    task_id = params.get("task_id", "default_task")
    filename = params.get("filename")

    if not filename:
        return {"success": False, "error": "Missing 'filename'"}

    try:
        session = default_sandbox_manager.get_or_create_session(execution_id, task_id, user_id)
        out_path = session.filesystem.resolve_path(filename)
        if not os.path.exists(out_path):
            return {"success": False, "error": f"Output file '{filename}' not found."}
        with open(out_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return {"success": True, "filename": filename, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}
