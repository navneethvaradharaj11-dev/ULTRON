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


class StartExecutionRequest(BaseModel):
    goal: str
    conversation_id: Optional[str] = None


class ExecutionResponse(BaseModel):
    id: str
    user_id: str
    goal: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ExecutionDetailResponse(ExecutionResponse):
    tasks: List[Dict[str, Any]]
    events: List[Dict[str, Any]]


class ApprovalResponseRequest(BaseModel):
    approval_id: str
    action: str  # "approved" or "denied"


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def start_execution(
    req: StartExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ExecutionRepository(db)
    execution = await repo.create_execution(
        user_id=current_user.id,
        goal=req.goal,
        conversation_id=req.conversation_id
    )

    # Build initial TaskGraph using PlannerAgent
    planner = PlannerAgent(ModelManager())
    plan = await planner.plan(req.goal)

    graph = TaskGraph(execution.id, req.goal)
    for idx, t_item in enumerate(plan.tasks):
        graph.add_task(TaskNode(
            task_id=t_item.id or f"task_{idx+1}",
            goal=t_item.goal,
            assigned_agent=t_item.assigned_agent,
            description=t_item.description,
            dependencies=t_item.dependencies,
            priority=t_item.priority
        ))

    return ExecutionResponse(
        id=execution.id,
        user_id=execution.user_id,
        goal=execution.goal,
        status=execution.status,
        created_at=execution.created_at.isoformat()
    )


@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ExecutionRepository(db)
    executions = await repo.get_user_executions(current_user.id)
    return [
        ExecutionResponse(
            id=e.id,
            user_id=e.user_id,
            goal=e.goal,
            status=e.status,
            created_at=e.created_at.isoformat(),
            started_at=e.started_at.isoformat() if e.started_at else None,
            completed_at=e.completed_at.isoformat() if e.completed_at else None
        )
        for e in executions
    ]


@router.get("/{execution_id}", response_model=ExecutionDetailResponse)
async def get_execution_detail(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ExecutionRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found or access denied")

    tasks = await repo.get_execution_tasks(execution_id)
    events = await repo.session.execute(
        repo.session.query(repo.session.models.ExecutionEvent)
        .where(repo.session.models.ExecutionEvent.execution_id == execution_id)
        .order_by(repo.session.models.ExecutionEvent.created_at.asc())
    ) if hasattr(repo.session, "query") else []

    return ExecutionDetailResponse(
        id=execution.id,
        user_id=execution.user_id,
        goal=execution.goal,
        status=execution.status,
        created_at=execution.created_at.isoformat(),
        started_at=execution.started_at.isoformat() if execution.started_at else None,
        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
        tasks=[
            {
                "id": t.id,
                "goal": t.goal,
                "assigned_agent": t.assigned_agent,
                "dependencies": t.dependencies_json,
                "status": t.status,
                "retry_count": t.retry_count,
                "max_retries": t.max_retries,
                "output_json": t.output_json
            }
            for t in tasks
        ],
        events=[]
    )


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
async def cancel_execution(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ExecutionRepository(db)
    execution = await repo.get_execution_by_id(execution_id)
    if not execution or execution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Execution not found")

    updated = await repo.update_execution_status(execution_id, "CANCELLED")
    tasks = await repo.get_execution_tasks(execution_id)
    for t in tasks:
        if t.status in ["PENDING", "RUNNING", "WAITING"]:
            await repo.update_task_status(t.id, "CANCELLED")

    return ExecutionResponse(
        id=updated.id,
        user_id=updated.user_id,
        goal=updated.goal,
        status=updated.status,
        created_at=updated.created_at.isoformat(),
        started_at=updated.started_at.isoformat() if updated.started_at else None,
        completed_at=updated.completed_at.isoformat() if updated.completed_at else None
    )


@router.post("/approve", response_model=Dict[str, Any])
async def respond_approval(
    req: ApprovalResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    manager = ApprovalManager(db)
    res = await manager.submit_response(req.approval_id, req.action)
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return {"status": "success", "approval_id": res.id, "action": res.status}
