import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.security.authentication import get_current_user
from app.database.models import User
from app.computer.computer_manager import computer_manager
from app.tools import computer_tools

logger = logging.getLogger("ULTRON.ComputerAPI")
router = APIRouter(prefix="/computer", tags=["Controlled Computer Interaction"])


class CreateSessionRequest(BaseModel):
    execution_id: str
    viewport_width: int = 1280
    viewport_height: int = 800


class ActionRequest(BaseModel):
    action_type: str
    target: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    confidence: float = 1.0


class ActionResponseRequest(BaseModel):
    action_id: str
    session_id: str


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_computer_session(req: CreateSessionRequest, current_user: User = Depends(get_current_user)):
    sess = computer_manager.create_session(
        user_id=current_user.id,
        execution_id=req.execution_id,
        viewport_width=req.viewport_width,
        viewport_height=req.viewport_height
    )
    return {
        "status": "success",
        "session_id": sess.session_id,
        "execution_id": sess.execution_id,
        "viewport": {"width": sess.viewport_width, "height": sess.viewport_height}
    }


@router.get("/sessions")
async def list_computer_sessions(current_user: User = Depends(get_current_user)):
    sessions = computer_manager.list_active_sessions(current_user.id)
    return [
        {
            "session_id": s.session_id,
            "execution_id": s.execution_id,
            "status": s.status,
            "viewport": {"width": s.viewport_width, "height": s.viewport_height},
            "created_at": s.created_at.isoformat()
        } for s in sessions
    ]


@router.get("/sessions/{session_id}")
async def get_computer_session(session_id: str, current_user: User = Depends(get_current_user)):
    sess = computer_manager.get_session(session_id, current_user.id)
    if not sess:
        raise HTTPException(status_code=404, detail="Computer session not found or access denied")
    return {
        "session_id": sess.session_id,
        "user_id": sess.user_id,
        "execution_id": sess.execution_id,
        "status": sess.status,
        "viewport": {"width": sess.viewport_width, "height": sess.viewport_height},
        "action_count": sess.action_count,
        "created_at": sess.created_at.isoformat()
    }


@router.post("/sessions/{session_id}/close")
async def close_computer_session(session_id: str, current_user: User = Depends(get_current_user)):
    success = computer_manager.close_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
    return {"status": "success", "message": f"Session '{session_id}' closed."}


@router.post("/sessions/{session_id}/actions")
async def execute_computer_action(session_id: str, req: ActionRequest, current_user: User = Depends(get_current_user)):
    sess = computer_manager.get_session(session_id, current_user.id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found or access denied")

    res = await computer_tools.computer_execute_action(
        session_id=session_id,
        user_id=current_user.id,
        action_type=req.action_type,
        target=req.target,
        parameters=req.parameters,
        confidence=req.confidence
    )
    return res


@router.post("/actions/approve")
async def approve_computer_action(req: ActionResponseRequest, current_user: User = Depends(get_current_user)):
    sess = computer_manager.get_session(req.session_id, current_user.id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
    return {
        "status": "APPROVED",
        "action_id": req.action_id,
        "session_id": req.session_id,
        "message": f"Action '{req.action_id}' explicitly approved by user."
    }


@router.post("/actions/reject")
async def reject_computer_action(req: ActionResponseRequest, current_user: User = Depends(get_current_user)):
    sess = computer_manager.get_session(req.session_id, current_user.id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found or access denied")
    return {
        "status": "REJECTED",
        "action_id": req.action_id,
        "session_id": req.session_id,
        "message": f"Action '{req.action_id}' rejected by user."
    }
