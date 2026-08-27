from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.approval_manager import ApprovalManager
from app.agents.planner import PlannerAgent
from app.ai.model_manager import ModelManager

router = APIRouter(prefix="/api/v1/executions", tags=["Executions"])


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------

class StartExecutionRequest(BaseModel):
    goal: str
    conversation_id: Optional[str] = None
    idempotency_key: Optional[str] = None  # Phase 2.5: client-supplied dedup key


class ExecutionResponse(BaseModel):
    id: str
    user_id: str
    goal: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    idempotency_key: Optional[str] = None


class TaskSummary(BaseModel):
    id: str
    goal: str
    assigned_agent: str
    dependencies: Optional[List[str]]
    status: str
    retry_count: int
    max_retries: int
    output_json: Optional[Dict[str, Any]]


class EventSummary(BaseModel):
    id: str
    event_type: str
    payload_json: Optional[Dict[str, Any]]
    created_at: str


class ExecutionDetailResponse(ExecutionResponse):
    tasks: List[TaskSummary]
    events: List[EventSummary]
    event_consistency: Optional[Dict[str, Any]] = None


class ApprovalResponseRequest(BaseModel):
    approval_id: str
    action: str  # "approved" or "denied"


class MetricsSummary(BaseModel):
    agent_name: str
    total_tasks: int
    completed: int
    failed: int
    total_duration_ms: int
    total_retries: int
    avg_review_confidence: float


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _serialize_execution(e) -> ExecutionResponse:
    return ExecutionResponse(
        id=e.id,
        user_id=e.user_id,
        goal=e.goal,
        status=e.status,
        created_at=e.created_at.isoformat(),
        started_at=e.started_at.isoformat() if e.started_at else None,
        completed_at=e.completed_at.isoformat() if e.completed_at else None,
        idempotency_key=e.idempotency_key,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def start_execution(
    req: StartExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new agentic execution (or return existing one if idempotency_key matches)."""
    repo = ExecutionRepository(db)
    execution = await repo.create_execution(
        user_id=current_user.id,
        goal=req.goal,
        conversation_id=req.conversation_id,
        idempotency_key=req.idempotency_key
    )
    return _serialize_execution(execution)


@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all executions for the authenticated user."""
    repo = ExecutionRepository(db)
    executions = await repo.get_user_executions(current_user.id)
    return [_serialize_execution(e) for e in executions]


@router.get("/metrics", response_model=List[MetricsSummary])
async def get_agent_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return aggregate per-agent performance metrics across all executions."""
    repo = ExecutionRepository(db)
    stats = await repo.get_aggregate_agent_metrics(current_user.id)
    return [MetricsSummary(**s) for s in stats]


@router.get("/{execution_id}", response_model=ExecutionDetailResponse)
async def get_execution_detail(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return full execution detail: tasks + ordered event timeline + consistency check."""
    repo = ExecutionRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found or access denied")

    tasks = await repo.get_execution_tasks(execution_id)
    events = await repo.get_execution_events(execution_id)
    consistency = await repo.verify_event_consistency(execution_id)

    return ExecutionDetailResponse(
        **_serialize_execution(execution).model_dump(),
        tasks=[
            TaskSummary(
                id=t.id,
                goal=t.goal,
                assigned_agent=t.assigned_agent,
                dependencies=t.dependencies_json,
                status=t.status,
                retry_count=t.retry_count,
                max_retries=t.max_retries,
                output_json=t.output_json
            )
            for t in tasks
        ],
        events=[
            EventSummary(
                id=e.id,
                event_type=e.event_type,
                payload_json=e.payload_json,
                created_at=e.created_at.isoformat()
            )
            for e in events
        ],
        event_consistency=consistency
    )


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
async def cancel_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel an active execution and all its pending/running tasks."""
    repo = ExecutionRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")

    updated = await repo.update_execution_status(execution_id, "CANCELLED")
    tasks = await repo.get_execution_tasks(execution_id)
    for t in tasks:
        if t.status in ("PENDING", "RUNNING", "WAITING"):
            await repo.update_task_status(t.id, "CANCELLED")

    return _serialize_execution(updated)


@router.post("/{execution_id}/resume", response_model=ExecutionResponse)
async def resume_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a RUNNING execution that was interrupted (e.g., process crash).

    The engine reconstructs the TaskGraph from DB state and re-runs all
    non-completed tasks. Already-COMPLETED tasks are preserved.
    """
    repo = ExecutionRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")
    if execution.status in ("COMPLETED", "FAILED", "CANCELLED"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot resume execution with status '{execution.status}'"
        )

    engine = AgentExecutionEngine(db=db)
    graph = await engine.rebuild_graph_from_db(execution_id)
    if not graph:
        raise HTTPException(status_code=400, detail="Could not rebuild execution graph from DB")

    # Fire-and-forget: consume the generator to trigger resumption
    # (caller gets immediate 200; events continue in background via WebSocket)
    events_consumed = 0
    async for _ in engine.run_execution(execution_id, graph, current_user.id):
        events_consumed += 1

    execution = await repo.get_execution_by_id(execution_id)
    return _serialize_execution(execution)


@router.post("/approve", response_model=Dict[str, Any])
async def respond_approval(
    req: ApprovalResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit user approval or denial for a pending sensitive tool call."""
    manager = ApprovalManager(db)
    res = await manager.submit_response(req.approval_id, req.action)
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return {"status": "success", "approval_id": res.id, "action": res.status}
