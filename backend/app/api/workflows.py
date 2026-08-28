import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.workflow_repo import WorkflowRepository
from app.orchestration.orchestrator import WorkflowOrchestrator
from app.orchestration.workflow_state import WorkflowState
from app.orchestration.approval_coordinator import ApprovalCoordinator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

class CreateWorkflowRequest(BaseModel):
    goal: str = Field(..., description="High-level autonomous workflow goal")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")

class ApprovalDecisionRequest(BaseModel):
    approval_id: str = Field(..., description="ID of approval request")
    approved: bool = Field(..., description="True to approve, False to deny")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    req: CreateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new autonomous workflow."""
    orchestrator = WorkflowOrchestrator(db)
    wf = await orchestrator.create_workflow(user_id=current_user.id, goal=req.goal)
    return {
        "workflow_id": wf.workflow_id,
        "goal": wf.goal,
        "state": wf.current_state.value,
        "created_at": wf.created_at.isoformat()
    }

@router.get("")
async def list_workflows(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List autonomous workflows for authenticated user."""
    repo = WorkflowRepository(db)
    workflows = await repo.list_workflows(user_id=current_user.id, limit=limit, offset=offset)
    return [
        {
            "workflow_id": w.id,
            "goal": w.goal,
            "state": w.current_state,
            "progress": w.progress,
            "current_step": w.current_step,
            "created_at": w.created_at.isoformat(),
            "updated_at": w.updated_at.isoformat()
        } for w in workflows
    ]

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow details by ID."""
    repo = WorkflowRepository(db)
    w = await repo.get_workflow(workflow_id, current_user.id)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return {
        "workflow_id": w.id,
        "goal": w.goal,
        "state": w.current_state,
        "progress": w.progress,
        "current_step": w.current_step,
        "retry_count": w.retry_count,
        "replan_count": w.replan_count,
        "created_at": w.created_at.isoformat(),
        "updated_at": w.updated_at.isoformat(),
        "started_at": w.started_at.isoformat() if w.started_at else None,
        "completed_at": w.completed_at.isoformat() if w.completed_at else None
    }

@router.post("/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start autonomous workflow execution."""
    repo = WorkflowRepository(db)
    w = await repo.get_workflow(workflow_id, current_user.id)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    orchestrator = WorkflowOrchestrator(db)
    events = []
    async for event in orchestrator.execute_workflow(workflow_id, current_user.id):
        events.append(event)

    return {
        "workflow_id": workflow_id,
        "status": "STARTED",
        "events_emitted": len(events),
        "final_event": events[-1] if events else None
    }

@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a running workflow."""
    repo = WorkflowRepository(db)
    w = await repo.update_workflow_state(workflow_id, current_user.id, WorkflowState.PAUSED.value)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return {"workflow_id": workflow_id, "state": w.current_state}

@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused workflow."""
    repo = WorkflowRepository(db)
    w = await repo.update_workflow_state(workflow_id, current_user.id, WorkflowState.RUNNING.value)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return {"workflow_id": workflow_id, "state": w.current_state}

@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a workflow."""
    repo = WorkflowRepository(db)
    w = await repo.update_workflow_state(workflow_id, current_user.id, WorkflowState.CANCELLED.value)
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return {"workflow_id": workflow_id, "state": w.current_state}

@router.post("/{workflow_id}/approve")
async def approve_workflow_action(
    workflow_id: str,
    req: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process human approval decision server-side."""
    coord = ApprovalCoordinator(db)
    try:
        res = await coord.process_approval_decision(
            workflow_id=workflow_id,
            approval_id=req.approval_id,
            user_id=current_user.id,
            approved=req.approved
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{workflow_id}/events")
async def get_workflow_events(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow event timeline."""
    repo = WorkflowRepository(db)
    events = await repo.get_events(workflow_id, current_user.id)
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "payload": e.payload_json,
            "created_at": e.created_at.isoformat()
        } for e in events
    ]

@router.get("/{workflow_id}/result")
async def get_workflow_result(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow final result."""
    repo = WorkflowRepository(db)
    res = await repo.get_result(workflow_id, current_user.id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow result not found")
    return {
        "id": res.id,
        "workflow_id": res.workflow_id,
        "summary": res.summary,
        "status": res.status,
        "confidence": res.confidence,
        "evidence": res.evidence_json,
        "tasks_completed": res.tasks_completed,
        "tasks_failed": res.tasks_failed,
        "warnings": res.warnings_json,
        "created_at": res.created_at.isoformat()
    }

@router.get("/{workflow_id}/artifacts")
async def get_workflow_artifacts(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workflow generated artifacts."""
    repo = WorkflowRepository(db)
    arts = await repo.get_artifacts(workflow_id, current_user.id)
    return [
        {
            "id": a.id,
            "filename": a.filename,
            "file_path": a.file_path,
            "artifact_type": a.artifact_type,
            "size_bytes": a.size_bytes,
            "created_at": a.created_at.isoformat()
        } for a in arts
    ]

@router.get("/{workflow_id}/steps")
async def get_workflow_steps(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get DAG task step graph for workflow."""
    repo = WorkflowRepository(db)
    steps = await repo.get_steps(workflow_id, current_user.id)
    return [
        {
            "id": s.id,
            "step_id": s.step_id,
            "name": s.name,
            "assigned_agent": s.assigned_agent,
            "status": s.status,
            "dependencies": s.dependencies_json or [],
            "input_data": s.input_data_json or {},
            "output_data": s.output_data_json or {},
            "error_message": s.error_message,
            "retry_count": s.retry_count,
            "duration_ms": s.duration_ms
        } for s in steps
    ]

@router.get("/{workflow_id}/approvals")
async def get_workflow_approvals(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending and historical approvals for workflow."""
    repo = WorkflowRepository(db)
    approvals = await repo.get_approvals(workflow_id, current_user.id)
    return [
        {
            "id": appr.id,
            "workflow_id": appr.workflow_id,
            "step_id": appr.step_id,
            "action_type": appr.action_type,
            "reason": appr.reason,
            "status": appr.status,
            "approved": appr.approved,
            "decision_by": appr.decision_by,
            "created_at": appr.created_at.isoformat(),
            "decided_at": appr.decided_at.isoformat() if appr.decided_at else None
        } for appr in approvals
    ]

@router.websocket("/ws/stream/{workflow_id}")
async def websocket_workflow_stream(
    websocket: WebSocket,
    workflow_id: str,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Real-time WebSocket event stream for workflow monitoring."""
    await websocket.accept()
    try:
        repo = WorkflowRepository(db)
        # Emit initial state snapshot
        events = await repo.get_events(workflow_id, "user_system")
        await websocket.send_json({
            "event_type": "initial_snapshot",
            "workflow_id": workflow_id,
            "events_count": len(events)
        })
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_json({"type": "pong"})
    except Exception as e:
        logger.info("WebSocket closed for workflow '%s': %s", workflow_id, e)

