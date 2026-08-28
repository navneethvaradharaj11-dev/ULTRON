from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.browser.browser_manager import browser_manager
from app.database.repositories.browser_repo import BrowserRepository

router = APIRouter(prefix="/api/v1/browser", tags=["Browser"])


class CreateSessionRequest(BaseModel):
    execution_id: Optional[str] = None
    initial_url: Optional[str] = None


class NavigateRequest(BaseModel):
    url: str


class ActionRequest(BaseModel):
    action_name: str
    params: Dict[str, Any] = {}


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new authenticated Playwright Chromium browser session."""
    session = await browser_manager.create_browser_session_async(
        user_id=current_user.id,
        execution_id=req.execution_id,
        db=db
    )
    if req.initial_url:
        await session.navigate(req.initial_url)


    repo = BrowserRepository(db)
    await repo.create_session(
        session_id=session.session_id,
        user_id=current_user.id,
        execution_id=req.execution_id,
        current_url=session.current_url
    )

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "execution_id": session.execution_id,
        "current_url": session.current_url,
        "status": session.status,
        "created_at": session.created_at.isoformat()
    }


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user)
):
    """List active browser sessions owned by the current user."""
    sessions = browser_manager.list_user_sessions(current_user.id)
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session_details(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get active session state enforcing user ownership authorization."""
    session, err = browser_manager.get_session(session_id, current_user.id)
    if err or not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if "ACCESS_DENIED" in str(err) else status.HTTP_404_NOT_FOUND,
            detail=err or "Browser session not found."
        )

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "execution_id": session.execution_id,
        "current_url": session.current_url,
        "status": session.status,
        "step_count": session.step_count,
        "current_page": session.current_page,
        "history": session.history
    }


@router.post("/sessions/{session_id}/navigate")
async def navigate_session(
    session_id: str,
    req: NavigateRequest,
    current_user: User = Depends(get_current_user)
):
    """Navigate to a target URL in an active session."""
    session, err = browser_manager.get_session(session_id, current_user.id)
    if err or not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN if "ACCESS_DENIED" in str(err) else status.HTTP_404_NOT_FOUND,
            detail=err or "Browser session not found."
        )

    success, page_data = await session.navigate(req.url)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=page_data.get("error", "Navigation failed."))

    return {"success": True, "session_id": session_id, "current_url": session.current_url, "page": page_data}


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close an active browser session."""
    success, message = browser_manager.close_browser_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)

    repo = BrowserRepository(db)
    await repo.close_session(session_id)

    return {"success": True, "session_id": session_id, "message": message}
