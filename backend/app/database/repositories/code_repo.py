import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.database.models import (
    CodeWorkspaceModel, CodeFileModel, CodeExecutionModel,
    CodeExecutionEventModel, CodeArtifactModel, CodeTestModel
)

logger = logging.getLogger("ULTRON.CodeRepository")


class CodeRepository:
    """Repository managing database persistence for Code Workspaces, Files, Executions, Events, Artifacts, and Tests."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Workspaces
    # ------------------------------------------------------------------
    async def create_workspace(
        self,
        user_id: str,
        name: str = "default_workspace",
        root_path: str = "",
        execution_id: Optional[str] = None,
        task_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> CodeWorkspaceModel:
        ws_id = workspace_id or str(uuid.uuid4())
        workspace = CodeWorkspaceModel(
            id=ws_id,
            user_id=user_id,
            execution_id=execution_id,
            task_id=task_id,
            name=name,
            root_path=root_path,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
        self.db.add(workspace)
        await self.db.commit()
        await self.db.refresh(workspace)
        return workspace

    async def get_workspace_by_id(self, workspace_id: str) -> Optional[CodeWorkspaceModel]:
        stmt = select(CodeWorkspaceModel).where(CodeWorkspaceModel.id == workspace_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_workspaces(self, user_id: str) -> List[CodeWorkspaceModel]:
        stmt = select(CodeWorkspaceModel).where(CodeWorkspaceModel.user_id == user_id).order_by(CodeWorkspaceModel.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # ------------------------------------------------------------------
    # Code Files
    # ------------------------------------------------------------------
    async def create_file(
        self,
        workspace_id: str,
        path: str,
        content: str = "",
        language: str = "text",
        file_id: Optional[str] = None
    ) -> CodeFileModel:
        fid = file_id or str(uuid.uuid4())
        size_bytes = len(content.encode("utf-8"))
        code_file = CodeFileModel(
            id=fid,
            workspace_id=workspace_id,
            path=path,
            language=language,
            content=content,
            size_bytes=size_bytes,
            created_at=datetime.utcnow()
        )
        self.db.add(code_file)
        await self.db.commit()
        await self.db.refresh(code_file)
        return code_file

    async def get_file_by_id(self, file_id: str) -> Optional[CodeFileModel]:
        stmt = select(CodeFileModel).where(CodeFileModel.id == file_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_file_by_path(self, workspace_id: str, path: str) -> Optional[CodeFileModel]:
        stmt = select(CodeFileModel).where(
            CodeFileModel.workspace_id == workspace_id,
            CodeFileModel.path == path
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_files(self, workspace_id: str) -> List[CodeFileModel]:
        stmt = select(CodeFileModel).where(CodeFileModel.workspace_id == workspace_id).order_by(CodeFileModel.path.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_file(self, file_id: str, content: str, language: Optional[str] = None) -> Optional[CodeFileModel]:
        code_file = await self.get_file_by_id(file_id)
        if not code_file:
            return None
        code_file.content = content
        code_file.size_bytes = len(content.encode("utf-8"))
        if language:
            code_file.language = language
        code_file.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(code_file)
        return code_file

    async def delete_file(self, file_id: str) -> bool:
        code_file = await self.get_file_by_id(file_id)
        if not code_file:
            return False
        await self.db.delete(code_file)
        await self.db.commit()
        return True

    # ------------------------------------------------------------------
    # Code Executions
    # ------------------------------------------------------------------
    async def create_code_execution(
        self,
        workspace_id: str,
        execution_id: str,
        task_id: str,
        user_id: str,
        language: str,
        runtime: str,
        agent: str = "code_agent",
        code_exec_id: Optional[str] = None
    ) -> CodeExecutionModel:
        cid = code_exec_id or str(uuid.uuid4())
        exec_model = CodeExecutionModel(
            id=cid,
            workspace_id=workspace_id,
            execution_id=execution_id,
            task_id=task_id,
            user_id=user_id,
            agent=agent,
            runtime=runtime,
            language=language,
            status="CREATED",
            created_at=datetime.utcnow()
        )
        self.db.add(exec_model)
        await self.db.commit()
        await self.db.refresh(exec_model)
        return exec_model

    async def get_code_execution_by_id(self, code_exec_id: str) -> Optional[CodeExecutionModel]:
        stmt = select(CodeExecutionModel).where(CodeExecutionModel.id == code_exec_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_code_executions(self, user_id: str) -> List[CodeExecutionModel]:
        stmt = select(CodeExecutionModel).where(CodeExecutionModel.user_id == user_id).order_by(CodeExecutionModel.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_code_execution_status(
        self,
        code_exec_id: str,
        status: str,
        exit_code: Optional[int] = None,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        duration_ms: Optional[int] = None,
        retry_count: Optional[int] = None
    ) -> Optional[CodeExecutionModel]:
        exec_model = await self.get_code_execution_by_id(code_exec_id)
        if not exec_model:
            return None
        exec_model.status = status
        if exit_code is not None:
            exec_model.exit_code = exit_code
        if stdout is not None:
            exec_model.stdout = stdout
            exec_model.output_size_bytes = len(stdout.encode("utf-8")) + (len(stderr.encode("utf-8")) if stderr else 0)
        if stderr is not None:
            exec_model.stderr = stderr
        if duration_ms is not None:
            exec_model.duration_ms = duration_ms
        if retry_count is not None:
            exec_model.retry_count = retry_count
        if status in ("COMPLETED", "FAILED", "TIMEOUT", "CANCELLED"):
            exec_model.completed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(exec_model)
        return exec_model

    # ------------------------------------------------------------------
    # Code Events & Artifacts & Tests
    # ------------------------------------------------------------------
    async def add_code_event(
        self,
        code_execution_id: str,
        execution_id: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> CodeExecutionEventModel:
        event = CodeExecutionEventModel(
            id=str(uuid.uuid4()),
            code_execution_id=code_execution_id,
            execution_id=execution_id,
            event_type=event_type,
            payload_json=payload,
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        await self.db.commit()
        return event

    async def create_artifact(
        self,
        code_execution_id: str,
        execution_id: str,
        task_id: str,
        filename: str,
        sandbox_path: str,
        mime_type: str = "text/plain",
        size_bytes: int = 0,
        hash_sha256: Optional[str] = None
    ) -> CodeArtifactModel:
        art = CodeArtifactModel(
            id=str(uuid.uuid4()),
            code_execution_id=code_execution_id,
            execution_id=execution_id,
            task_id=task_id,
            filename=filename,
            sandbox_path=sandbox_path,
            mime_type=mime_type,
            size_bytes=size_bytes,
            hash_sha256=hash_sha256,
            created_at=datetime.utcnow()
        )
        self.db.add(art)
        # increment artifact count
        exec_model = await self.get_code_execution_by_id(code_execution_id)
        if exec_model:
            exec_model.artifact_count += 1
        await self.db.commit()
        await self.db.refresh(art)
        return art

    async def list_artifacts(self, code_execution_id: str) -> List[CodeArtifactModel]:
        stmt = select(CodeArtifactModel).where(CodeArtifactModel.code_execution_id == code_execution_id)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def record_test(
        self,
        code_execution_id: str,
        test_name: str,
        framework: str,
        status: str,
        output: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> CodeTestModel:
        test_item = CodeTestModel(
            id=str(uuid.uuid4()),
            code_execution_id=code_execution_id,
            test_name=test_name,
            framework=framework,
            status=status,
            output=output,
            duration_ms=duration_ms,
            created_at=datetime.utcnow()
        )
        self.db.add(test_item)
        await self.db.commit()
        await self.db.refresh(test_item)
        return test_item
