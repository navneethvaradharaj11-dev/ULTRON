import uuid
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.code_repo import CodeRepository
from app.agents.code_agent import CodeAgent
from app.ai.model_manager import ModelManager
from app.sandbox.sandbox_manager import default_sandbox_manager, SandboxUnavailableError
from app.engine.execution_engine import AgentExecutionEngine

logger = logging.getLogger("ULTRON.API.Code")

router = APIRouter(prefix="/api/v1/code", tags=["Code Intelligence & Sandbox"])


# ------------------------------------------------------------------
# Request & Response Schemas
# ------------------------------------------------------------------
class CreateWorkspaceRequest(BaseModel):
    name: str = Field("default_workspace", description="Workspace name")
    execution_id: Optional[str] = None
    task_id: Optional[str] = None


class CreateFileRequest(BaseModel):
    path: str = Field(..., description="Relative file path in workspace")
    content: str = Field("", description="Source code or text content")
    language: str = Field("text", description="Programming language")


class UpdateFileRequest(BaseModel):
    content: str = Field(..., description="Updated code content")
    language: Optional[str] = None


class CodeExecutionRequest(BaseModel):
    workspace_id: str
    execution_id: str
    task_id: str
    language: str
    entrypoint: str
    args: Optional[List[str]] = None


class CodeTestRequest(BaseModel):
    workspace_id: str
    execution_id: str
    task_id: str
    language: str
    test_file: str


# ------------------------------------------------------------------
# Workspaces
# ------------------------------------------------------------------
@router.post("/workspaces", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    req: CreateWorkspaceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.create_workspace(
        user_id=current_user.id,
        name=req.name,
        execution_id=req.execution_id,
        task_id=req.task_id
    )
    return {
        "id": workspace.id,
        "name": workspace.name,
        "user_id": workspace.user_id,
        "status": workspace.status,
        "created_at": workspace.created_at.isoformat()
    }


@router.get("/workspaces")
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspaces = await repo.list_workspaces(user_id=current_user.id)
    return [
        {
            "id": w.id,
            "name": w.name,
            "execution_id": w.execution_id,
            "status": w.status,
            "created_at": w.created_at.isoformat()
        }
        for w in workspaces
    ]


@router.get("/workspaces/{id}")
async def get_workspace(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")
    files = await repo.list_files(id)
    return {
        "id": workspace.id,
        "name": workspace.name,
        "status": workspace.status,
        "files": [{"id": f.id, "path": f.path, "language": f.language, "size_bytes": f.size_bytes} for f in files]
    }


# ------------------------------------------------------------------
# Files
# ------------------------------------------------------------------
@router.post("/workspaces/{id}/files", status_code=status.HTTP_201_CREATED)
async def create_file(
    id: str,
    req: CreateFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")

    code_file = await repo.create_file(
        workspace_id=id,
        path=req.path,
        content=req.content,
        language=req.language
    )
    return {
        "id": code_file.id,
        "workspace_id": code_file.workspace_id,
        "path": code_file.path,
        "language": code_file.language,
        "size_bytes": code_file.size_bytes
    }


@router.get("/workspaces/{id}/files")
async def list_files(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")
    files = await repo.list_files(id)
    return [{"id": f.id, "path": f.path, "language": f.language, "size_bytes": f.size_bytes} for f in files]


@router.put("/workspaces/{id}/files/{file_id}")
async def update_file(
    id: str,
    file_id: str,
    req: UpdateFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")

    code_file = await repo.update_file(file_id=file_id, content=req.content, language=req.language)
    if not code_file:
        raise HTTPException(status_code=404, detail="File not found")

    return {"id": code_file.id, "path": code_file.path, "size_bytes": code_file.size_bytes}


@router.delete("/workspaces/{id}/files/{file_id}")
async def delete_file(
    id: str,
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")

    success = await repo.delete_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    return {"success": True, "file_id": file_id}


# ------------------------------------------------------------------
# Execution & Testing
# ------------------------------------------------------------------
@router.post("/execute")
async def execute_code(
    req: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(req.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")

    try:
        session = default_sandbox_manager.get_or_create_session(
            execution_id=req.execution_id,
            task_id=req.task_id,
            user_id=current_user.id
        )
    except SandboxUnavailableError as se:
        raise HTTPException(status_code=503, detail=str(se))

    exec_record = await repo.create_code_execution(
        workspace_id=req.workspace_id,
        execution_id=req.execution_id,
        task_id=req.task_id,
        user_id=current_user.id,
        language=req.language,
        runtime=req.language
    )

    res = session.execute_code(req.language, req.entrypoint, args=req.args)

    await repo.update_code_execution_status(
        code_exec_id=exec_record.id,
        status=res.status,
        exit_code=res.exit_code,
        stdout=res.stdout,
        stderr=res.stderr,
        duration_ms=res.duration_ms
    )

    return {
        "code_execution_id": exec_record.id,
        "status": res.status,
        "exit_code": res.exit_code,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "duration_ms": res.duration_ms
    }


@router.get("/executions")
async def list_executions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    executions = await repo.list_code_executions(user_id=current_user.id)
    return [
        {
            "id": e.id,
            "workspace_id": e.workspace_id,
            "execution_id": e.execution_id,
            "language": e.language,
            "status": e.status,
            "exit_code": e.exit_code,
            "duration_ms": e.duration_ms,
            "created_at": e.created_at.isoformat()
        }
        for e in executions
    ]


@router.get("/executions/{id}")
async def get_execution(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    e = await repo.get_code_execution_by_id(id)
    if not e or e.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found or unauthorized")
    return {
        "id": e.id,
        "workspace_id": e.workspace_id,
        "execution_id": e.execution_id,
        "language": e.language,
        "status": e.status,
        "exit_code": e.exit_code,
        "stdout": e.stdout,
        "stderr": e.stderr,
        "duration_ms": e.duration_ms,
        "retry_count": e.retry_count,
        "created_at": e.created_at.isoformat()
    }


@router.post("/executions/{id}/cancel")
async def cancel_execution(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = AgentExecutionEngine(db)
    res = await engine.cancel_execution(execution_id=id, user_id=current_user.id)
    return res


@router.post("/test")
async def test_code(
    req: CodeTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    workspace = await repo.get_workspace_by_id(req.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found or unauthorized")

    try:
        session = default_sandbox_manager.get_or_create_session(
            execution_id=req.execution_id,
            task_id=req.task_id,
            user_id=current_user.id
        )
    except SandboxUnavailableError as se:
        raise HTTPException(status_code=503, detail=str(se))

    exec_record = await repo.create_code_execution(
        workspace_id=req.workspace_id,
        execution_id=req.execution_id,
        task_id=req.task_id,
        user_id=current_user.id,
        language=req.language,
        runtime=req.language
    )

    res = session.run_tests(req.language, req.test_file)

    test_model = await repo.record_test(
        code_execution_id=exec_record.id,
        test_name=req.test_file,
        framework=req.language,
        status="PASSED" if res.status == "COMPLETED" else "FAILED",
        output=res.stdout + "\n" + res.stderr,
        duration_ms=res.duration_ms
    )

    return {
        "test_id": test_model.id,
        "status": test_model.status,
        "stdout": res.stdout,
        "stderr": res.stderr,
        "duration_ms": res.duration_ms
    }


@router.get("/executions/{id}/artifacts")
async def list_artifacts(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = CodeRepository(db)
    e = await repo.get_code_execution_by_id(id)
    if not e or e.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found or unauthorized")
    artifacts = await repo.list_artifacts(id)
    return [
        {
            "id": a.id,
            "filename": a.filename,
            "mime_type": a.mime_type,
            "size_bytes": a.size_bytes,
            "hash_sha256": a.hash_sha256,
            "created_at": a.created_at.isoformat()
        }
        for a in artifacts
    ]
