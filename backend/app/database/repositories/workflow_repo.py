import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import (
    WorkflowModel,
    WorkflowStepModel,
    WorkflowEventModel,
    WorkflowCheckpointModel,
    WorkflowFailureModel,
    WorkflowApprovalModel,
    WorkflowResultModel,
    WorkflowArtifactModel,
    generate_uuid
)

logger = logging.getLogger(__name__)

class WorkflowRepository:
    """Repository handling all Phase 7 database operations with tenant ownership enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(
        self,
        user_id: str,
        goal: str,
        execution_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> WorkflowModel:
        workflow = WorkflowModel(
            id=generate_uuid(),
            user_id=user_id,
            execution_id=execution_id,
            goal=goal,
            strategy_id=strategy_id,
            current_state="CREATED",
            progress=0.0,
            metadata_json=metadata_json or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def get_workflow(self, workflow_id: str, user_id: str) -> Optional[WorkflowModel]:
        stmt = select(WorkflowModel).where(
            WorkflowModel.id == workflow_id,
            WorkflowModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_workflows(self, user_id: str, limit: int = 50, offset: int = 0) -> List[WorkflowModel]:
        stmt = select(WorkflowModel).where(
            WorkflowModel.user_id == user_id
        ).order_by(WorkflowModel.created_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_workflow_state(
        self,
        workflow_id: str,
        user_id: str,
        state: str,
        progress: Optional[float] = None,
        current_step: Optional[str] = None
    ) -> Optional[WorkflowModel]:
        workflow = await self.get_workflow(workflow_id, user_id)
        if not workflow:
            return None

        workflow.current_state = state
        workflow.updated_at = datetime.utcnow()
        if progress is not None:
            workflow.progress = progress
        if current_step is not None:
            workflow.current_step = current_step

        if state == "RUNNING" and not workflow.started_at:
            workflow.started_at = datetime.utcnow()
        elif state in ("COMPLETED", "FAILED", "CANCELLED"):
            workflow.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def create_step(
        self,
        workflow_id: str,
        step_id: str,
        name: str,
        assigned_agent: str,
        dependencies: Optional[List[str]] = None,
        input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowStepModel:
        step = WorkflowStepModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            step_id=step_id,
            name=name,
            assigned_agent=assigned_agent,
            status="PENDING",
            dependencies_json=dependencies or [],
            input_data_json=input_data or {},
            retry_count=0,
            duration_ms=0
        )
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def update_step(
        self,
        workflow_id: str,
        step_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> Optional[WorkflowStepModel]:
        stmt = select(WorkflowStepModel).where(
            WorkflowStepModel.workflow_id == workflow_id,
            WorkflowStepModel.step_id == step_id
        )
        res = await self.db.execute(stmt)
        step = res.scalar_one_or_none()
        if not step:
            return None

        step.status = status
        if output_data is not None:
            step.output_data_json = output_data
        if error_message is not None:
            step.error_message = error_message
        if duration_ms is not None:
            step.duration_ms = duration_ms

        if status == "RUNNING" and not step.started_at:
            step.started_at = datetime.utcnow()
        elif status in ("COMPLETED", "FAILED", "CANCELLED"):
            step.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def create_event(
        self,
        workflow_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None
    ) -> WorkflowEventModel:
        event = WorkflowEventModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            event_type=event_type,
            payload_json=payload or {},
            created_at=datetime.utcnow()
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_events(self, workflow_id: str, user_id: str) -> List[WorkflowEventModel]:
        wf = await self.get_workflow(workflow_id, user_id)
        if not wf:
            return []
        stmt = select(WorkflowEventModel).where(
            WorkflowEventModel.workflow_id == workflow_id
        ).order_by(WorkflowEventModel.created_at.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_checkpoint(
        self,
        workflow_id: str,
        checkpoint_name: str,
        state_snapshot: Dict[str, Any]
    ) -> WorkflowCheckpointModel:
        cp = WorkflowCheckpointModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            checkpoint_name=checkpoint_name,
            state_snapshot_json=state_snapshot,
            created_at=datetime.utcnow()
        )
        self.db.add(cp)
        await self.db.commit()
        await self.db.refresh(cp)
        return cp

    async def get_latest_checkpoint(self, workflow_id: str, user_id: str) -> Optional[WorkflowCheckpointModel]:
        wf = await self.get_workflow(workflow_id, user_id)
        if not wf:
            return None
        stmt = select(WorkflowCheckpointModel).where(
            WorkflowCheckpointModel.workflow_id == workflow_id
        ).order_by(WorkflowCheckpointModel.created_at.desc()).limit(1)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def record_failure(
        self,
        workflow_id: str,
        failure_type: str,
        error_message: str,
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True
    ) -> WorkflowFailureModel:
        failure = WorkflowFailureModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            task_id=task_id,
            agent=agent,
            failure_type=failure_type,
            error_message=error_message,
            context_json=context or {},
            recoverable=recoverable,
            created_at=datetime.utcnow()
        )
        self.db.add(failure)
        await self.db.commit()
        await self.db.refresh(failure)
        return failure

    async def create_approval(
        self,
        workflow_id: str,
        task_id: str,
        action_type: str,
        details: Optional[Dict[str, Any]] = None
    ) -> WorkflowApprovalModel:
        appr = WorkflowApprovalModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            task_id=task_id,
            action_type=action_type,
            details_json=details or {},
            status="PENDING",
            created_at=datetime.utcnow()
        )
        self.db.add(appr)
        await self.db.commit()
        await self.db.refresh(appr)
        return appr

    async def update_approval(
        self,
        workflow_id: str,
        approval_id: str,
        user_id: str,
        status: str
    ) -> Optional[WorkflowApprovalModel]:
        wf = await self.get_workflow(workflow_id, user_id)
        if not wf:
            return None
        stmt = select(WorkflowApprovalModel).where(
            WorkflowApprovalModel.id == approval_id,
            WorkflowApprovalModel.workflow_id == workflow_id
        )
        res = await self.db.execute(stmt)
        appr = res.scalar_one_or_none()
        if not appr:
            return None

        appr.status = status
        appr.decided_by = user_id
        appr.decided_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(appr)
        return appr

    async def create_result(
        self,
        workflow_id: str,
        summary: str,
        status: str,
        confidence: float = 1.0,
        evidence: Optional[Dict[str, Any]] = None,
        tasks_completed: int = 0,
        tasks_failed: int = 0,
        warnings: Optional[List[str]] = None
    ) -> WorkflowResultModel:
        result = WorkflowResultModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            summary=summary,
            status=status,
            confidence=confidence,
            evidence_json=evidence or {},
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            warnings_json=warnings or [],
            created_at=datetime.utcnow()
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_result(self, workflow_id: str, user_id: str) -> Optional[WorkflowResultModel]:
        wf = await self.get_workflow(workflow_id, user_id)
        if not wf:
            return None
        stmt = select(WorkflowResultModel).where(
            WorkflowResultModel.workflow_id == workflow_id
        ).order_by(WorkflowResultModel.created_at.desc()).limit(1)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_artifact(
        self,
        workflow_id: str,
        filename: str,
        file_path: str,
        artifact_type: str,
        size_bytes: int = 0
    ) -> WorkflowArtifactModel:
        art = WorkflowArtifactModel(
            id=generate_uuid(),
            workflow_id=workflow_id,
            filename=filename,
            file_path=file_path,
            artifact_type=artifact_type,
            size_bytes=size_bytes,
            created_at=datetime.utcnow()
        )
        self.db.add(art)
        await self.db.commit()
        await self.db.refresh(art)
        return art

    async def get_artifacts(self, workflow_id: str, user_id: str) -> List[WorkflowArtifactModel]:
        wf = await self.get_workflow(workflow_id, user_id)
        if not wf:
            return []
        stmt = select(WorkflowArtifactModel).where(
            WorkflowArtifactModel.workflow_id == workflow_id
        ).order_by(WorkflowArtifactModel.created_at.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
