import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.database.models import (
    Execution, ExecutionTask, ExecutionEvent, Approval, ExecutionMetrics
)

# ---------------------------------------------------------------------------
# Valid state-machine transitions for Execution and ExecutionTask
# ---------------------------------------------------------------------------
EXECUTION_TRANSITIONS: Dict[str, set] = {
    "PENDING":    {"RUNNING", "CANCELLED"},
    "RUNNING":    {"COMPLETED", "FAILED", "CANCELLED"},
    "COMPLETED":  set(),  # terminal
    "FAILED":     set(),  # terminal
    "CANCELLED":  set(),  # terminal
}

TASK_TRANSITIONS: Dict[str, set] = {
    "PENDING":          {"RUNNING", "CANCELLED"},
    "RUNNING":          {"COMPLETED", "FAILED", "CANCELLED", "REQUIRES_APPROVAL", "WAITING"},
    "WAITING":          {"RUNNING", "CANCELLED"},
    "REQUIRES_APPROVAL": {"RUNNING", "CANCELLED"},
    "COMPLETED":        set(),  # terminal
    "FAILED":           set(),  # terminal
    "CANCELLED":        set(),  # terminal
}


def validate_execution_transition(current: str, next_status: str) -> bool:
    """Return True if the status transition is legal for an Execution."""
    return next_status in EXECUTION_TRANSITIONS.get(current, set())


def validate_task_transition(current: str, next_status: str) -> bool:
    """Return True if the status transition is legal for an ExecutionTask."""
    return next_status in TASK_TRANSITIONS.get(current, set())


class ExecutionRepository:
    """Data Access Object for Phase 2/2.5 Executions, Tasks, Events, Approvals, Metrics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Execution CRUD
    # ------------------------------------------------------------------

    async def create_execution(
        self,
        user_id: str,
        goal: str,
        conversation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Execution:
        """Create execution, honouring idempotency_key to prevent duplicates.

        If idempotency_key is supplied and an execution with that key already
        exists, the existing record is returned without creating a duplicate.
        """
        if idempotency_key:
            existing = await self.get_by_idempotency_key(idempotency_key)
            if existing:
                return existing

        execution = Execution(
            user_id=user_id,
            conversation_id=conversation_id,
            goal=goal,
            status="PENDING",
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow()
        )
        self.session.add(execution)
        try:
            await self.session.commit()
        except IntegrityError:
            # Race condition — another request committed the same key first
            await self.session.rollback()
            if idempotency_key:
                existing = await self.get_by_idempotency_key(idempotency_key)
                if existing:
                    return existing
            raise
        await self.session.refresh(execution)
        return execution

    async def get_by_idempotency_key(self, key: str) -> Optional[Execution]:
        stmt = select(Execution).where(Execution.idempotency_key == key)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_execution_by_id(self, execution_id: str) -> Optional[Execution]:
        stmt = select(Execution).where(Execution.id == execution_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_user_executions(self, user_id: str) -> List[Execution]:
        stmt = (
            select(Execution)
            .where(Execution.user_id == user_id)
            .order_by(Execution.created_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_execution_status(
        self, execution_id: str, status: str, *, force: bool = False
    ) -> Optional[Execution]:
        """Update execution status, enforcing state machine unless force=True."""
        execution = await self.get_execution_by_id(execution_id)
        if not execution:
            return None
        if not force and not validate_execution_transition(execution.status, status):
            # Silently skip illegal no-op transitions (e.g. FAILED→FAILED during cancellation)
            return execution
        execution.status = status
        if status == "RUNNING" and not execution.started_at:
            execution.started_at = datetime.utcnow()
        elif status in ("COMPLETED", "FAILED", "CANCELLED"):
            execution.completed_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    # ------------------------------------------------------------------
    # ExecutionTask CRUD
    # ------------------------------------------------------------------

    async def create_execution_task(
        self,
        execution_id: str,
        goal: str,
        assigned_agent: str,
        description: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        priority: str = "medium",
        max_retries: int = 3,
        task_id: Optional[str] = None
    ) -> ExecutionTask:
        t_id = task_id or str(uuid.uuid4())
        if task_id:
            stmt = select(ExecutionTask).where(ExecutionTask.id == task_id)
            res = await self.session.execute(stmt)
            if res.scalars().first():
                t_id = str(uuid.uuid4())

        task = ExecutionTask(
            id=t_id,
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
        stmt = (
            select(ExecutionTask)
            .where(ExecutionTask.execution_id == execution_id)
            .order_by(ExecutionTask.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        output_json: Optional[Dict[str, Any]] = None,
        *,
        force: bool = False
    ) -> Optional[ExecutionTask]:
        """Update task status, enforcing state machine unless force=True."""
        stmt = select(ExecutionTask).where(ExecutionTask.id == task_id)
        res = await self.session.execute(stmt)
        task = res.scalars().first()
        if not task:
            return None
        if not force and not validate_task_transition(task.status, status):
            return task  # skip illegal transition silently
        task.status = status
        if output_json is not None:
            task.output_json = output_json
        if status == "RUNNING" and not task.started_at:
            task.started_at = datetime.utcnow()
        elif status in ("COMPLETED", "FAILED", "CANCELLED"):
            task.completed_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    # ------------------------------------------------------------------
    # Phase 2.5: resume_execution — rebuild TaskGraph from DB state
    # ------------------------------------------------------------------

    async def get_incomplete_tasks(self, execution_id: str) -> List[ExecutionTask]:
        """Return tasks that are not yet in a terminal state (for crash recovery)."""
        stmt = (
            select(ExecutionTask)
            .where(
                ExecutionTask.execution_id == execution_id,
                ExecutionTask.status.notin_(["COMPLETED", "CANCELLED", "FAILED"])
            )
            .order_by(ExecutionTask.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def reset_running_tasks_to_pending(self, execution_id: str) -> int:
        """Reset all RUNNING tasks back to PENDING so they can be re-executed on resume.

        Returns number of tasks reset.
        """
        tasks = await self.get_execution_tasks(execution_id)
        reset_count = 0
        for t in tasks:
            if t.status == "RUNNING":
                t.status = "PENDING"
                t.started_at = None
                reset_count += 1
        if reset_count:
            await self.session.commit()
        return reset_count

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    async def add_event(
        self, execution_id: str, event_type: str, payload_json: Dict[str, Any]
    ) -> ExecutionEvent:
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

    async def get_execution_events(self, execution_id: str) -> List[ExecutionEvent]:
        stmt = (
            select(ExecutionEvent)
            .where(ExecutionEvent.execution_id == execution_id)
            .order_by(ExecutionEvent.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def verify_event_consistency(self, execution_id: str) -> Dict[str, Any]:
        """Verify event sequence integrity for an execution.

        Checks that:
        - execution_started exists and comes first
        - every task_started has a matching task_completed or task_failed
        - execution_completed or execution_failed exists at end

        Returns a dict with 'valid' bool and 'issues' list.
        """
        events = await self.get_execution_events(execution_id)
        event_types = [e.event_type for e in events]
        issues: List[str] = []

        if not event_types:
            return {"valid": False, "issues": ["No events found for execution"]}

        if event_types[0] != "execution_started":
            issues.append(f"First event is '{event_types[0]}', expected 'execution_started'")

        # Every task_started must be matched by task_completed or task_failed
        started_tasks = set()
        ended_tasks = set()
        for e in events:
            payload = e.payload_json or {}
            tid = payload.get("task_id")
            if e.event_type == "task_started" and tid:
                started_tasks.add(tid)
            elif e.event_type in ("task_completed", "task_failed") and tid:
                ended_tasks.add(tid)

        unmatched = started_tasks - ended_tasks
        if unmatched:
            issues.append(f"Tasks started but not ended: {unmatched}")

        terminal_events = {"execution_completed", "execution_failed"}
        if not any(et in terminal_events for et in event_types):
            issues.append("No terminal event (execution_completed/execution_failed) found")

        return {"valid": len(issues) == 0, "issues": issues}

    # ------------------------------------------------------------------
    # Approvals
    # ------------------------------------------------------------------

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

    async def update_approval_status(
        self, approval_id: str, status: str
    ) -> Optional[Approval]:
        stmt = select(Approval).where(Approval.id == approval_id)
        res = await self.session.execute(stmt)
        approval = res.scalars().first()
        if approval:
            approval.status = status
            await self.session.commit()
            await self.session.refresh(approval)
        return approval



    async def get_pending_approval(self, execution_id: str) -> Optional[Approval]:
        stmt = select(Approval).where(Approval.execution_id == execution_id, Approval.status == "pending")
        res = await self.session.execute(stmt)
        return res.scalars().first()



    # ------------------------------------------------------------------
    # Phase 2.5: Metrics
    # ------------------------------------------------------------------

    async def record_metrics(
        self,
        execution_id: str,
        task_id: Optional[str],
        agent_name: str,
        duration_ms: int,
        status: str,
        retry_count: int = 0,
        tools_used: Optional[List[str]] = None,
        review_status: Optional[str] = None,
        review_confidence: float = 0.0
    ) -> ExecutionMetrics:
        metric = ExecutionMetrics(
            execution_id=execution_id,
            task_id=task_id,
            agent_name=agent_name,
            duration_ms=duration_ms,
            status=status,
            retry_count=retry_count,
            tools_used_json=tools_used or [],
            review_status=review_status,
            review_confidence=int(review_confidence * 100),
            created_at=datetime.utcnow()
        )
        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)
        return metric

    async def get_execution_metrics(self, execution_id: str) -> List[ExecutionMetrics]:
        stmt = (
            select(ExecutionMetrics)
            .where(ExecutionMetrics.execution_id == execution_id)
            .order_by(ExecutionMetrics.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_aggregate_agent_metrics(self, user_id: str) -> List[Dict[str, Any]]:
        """Aggregate per-agent stats across all of a user's executions."""
        executions = await self.get_user_executions(user_id)
        exec_ids = [e.id for e in executions]
        if not exec_ids:
            return []

        all_metrics: List[ExecutionMetrics] = []
        for eid in exec_ids:
            all_metrics.extend(await self.get_execution_metrics(eid))

        # Group by agent name
        agent_stats: Dict[str, Dict[str, Any]] = {}
        for m in all_metrics:
            if m.agent_name not in agent_stats:
                agent_stats[m.agent_name] = {
                    "agent_name": m.agent_name,
                    "total_tasks": 0,
                    "completed": 0,
                    "failed": 0,
                    "total_duration_ms": 0,
                    "total_retries": 0,
                    "avg_review_confidence": 0.0,
                    "confidence_samples": 0,
                }
            s = agent_stats[m.agent_name]
            s["total_tasks"] += 1
            s["total_duration_ms"] += m.duration_ms
            s["total_retries"] += m.retry_count
            if m.status == "COMPLETED":
                s["completed"] += 1
            elif m.status == "FAILED":
                s["failed"] += 1
            if m.review_confidence and m.review_confidence > 0:
                s["avg_review_confidence"] = (
                    (s["avg_review_confidence"] * s["confidence_samples"] + m.review_confidence)
                    / (s["confidence_samples"] + 1)
                )
                s["confidence_samples"] += 1

        return list(agent_stats.values())
