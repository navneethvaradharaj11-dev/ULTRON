from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Execution, ExecutionTask, ExecutionEvent, Approval


class ExecutionRepository:
    """Data Access Object for Phase 2 Executions, Tasks, Events, and Approvals."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_execution(
        self,
        user_id: str,
        goal: str,
        conversation_id: Optional[str] = None
    ) -> Execution:
        execution = Execution(
            user_id=user_id,
            conversation_id=conversation_id,
            goal=goal,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        self.session.add(execution)
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def get_execution_by_id(self, execution_id: str) -> Optional[Execution]:
        stmt = select(Execution).where(Execution.id == execution_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_user_executions(self, user_id: str) -> List[Execution]:
        stmt = select(Execution).where(Execution.user_id == user_id).order_by(Execution.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_execution_status(self, execution_id: str, status: str) -> Optional[Execution]:
        execution = await self.get_execution_by_id(execution_id)
        if execution:
            execution.status = status
            if status == "RUNNING" and not execution.started_at:
                execution.started_at = datetime.utcnow()
            elif status in ["COMPLETED", "FAILED", "CANCELLED"]:
                execution.completed_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(execution)
        return execution

    async def create_execution_task(
        self,
        execution_id: str,
        goal: str,
        assigned_agent: str,
        description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        priority: str = "medium",
        max_retries: int = 3
    ) -> ExecutionTask:
        task = ExecutionTask(
            execution_id=execution_id,
            goal=goal,
            description=description,
            assigned_agent=assigned_agent,
            dependencies_json=dependencies or [],
            status="PENDING",
            priority=priority,
            max_retries=max_retries,
            created_at=datetime.utcnow()
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_execution_tasks(self, execution_id: str) -> List[ExecutionTask]:
        stmt = select(ExecutionTask).where(ExecutionTask.execution_id == execution_id).order_by(ExecutionTask.created_at.asc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        output_json: Optional[Dict[str, Any]] = None
    ) -> Optional[ExecutionTask]:
        stmt = select(ExecutionTask).where(ExecutionTask.id == task_id)
        res = await self.session.execute(stmt)
        task = res.scalars().first()
        if task:
            task.status = status
            if output_json is not None:
                task.output_json = output_json
            if status == "RUNNING" and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status in ["COMPLETED", "FAILED", "CANCELLED"]:
                task.completed_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def add_event(self, execution_id: str, event_type: str, payload_json: Dict[str, Any]) -> ExecutionEvent:
        event = ExecutionEvent(
            execution_id=execution_id,
            event_type=event_type,
            payload_json=payload_json,
            created_at=datetime.utcnow()
        )
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def create_approval_request(
        self,
        execution_id: str,
        task_id: str,
        tool_name: str,
        params_json: Dict[str, Any]
    ) -> Approval:
        approval = Approval(
            execution_id=execution_id,
            task_id=task_id,
            tool_name=tool_name,
            params_json=params_json,
            status="pending"
        )
        self.session.add(approval)
        await self.session.commit()
        await self.session.refresh(approval)
        return approval

    async def update_approval_status(self, approval_id: str, status: str) -> Optional[Approval]:
        stmt = select(Approval).where(Approval.id == approval_id)
        res = await self.session.execute(stmt)
        approval = res.scalars().first()
        if approval:
            approval.status = status
            await self.session.commit()
            await self.session.refresh(approval)
        return approval
