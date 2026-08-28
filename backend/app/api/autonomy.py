import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.autonomy.autonomy_manager import AutonomyManager
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.security.autonomy_security import AutonomySecurityValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/autonomy", tags=["autonomy"])


class CreateRuleRequest(BaseModel):
    name: str = Field(..., description="Rule name")
    goal_template: str = Field(..., description="Goal template to execute")
    trigger_type: str = Field(default="SCHEDULE", description="Trigger type")
    trigger_config: Optional[Dict[str, Any]] = Field(default=None, description="Trigger configuration")
    description: Optional[str] = Field(default=None, description="Description")
    priority: str = Field(default="MEDIUM", description="Priority level")
    autonomy_level: str = Field(default="LEVEL_1", description="Autonomy level (LEVEL_0 to LEVEL_4)")
    cooldown_seconds: int = Field(default=300, description="Cooldown interval in seconds")


class TriggerTestRequest(BaseModel):
    event_type: str = Field(default="MANUAL", description="Event type")
    source: str = Field(default="user_test", description="Event source")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Event payload")


@router.post("/rules", status_code=status.HTTP_201_CREATED)
async def create_rule(
    req: CreateRuleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new proactive autonomy rule."""
    manager = AutonomyManager(db)
    return await manager.create_rule(
        user_id=current_user.id,
        name=req.name,
        goal_template=req.goal_template,
        trigger_type=req.trigger_type,
        trigger_config=req.trigger_config,
        description=req.description,
        priority=req.priority,
        autonomy_level=req.autonomy_level,
        cooldown_seconds=req.cooldown_seconds
    )


@router.get("/rules")
async def list_rules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List autonomy rules for authenticated user."""
    repo = AutonomyRepository(db)
    rules = await repo.list_rules(user_id=current_user.id)
    return [
        {
            "rule_id": r.id,
            "name": r.name,
            "description": r.description,
            "enabled": r.enabled,
            "trigger_type": r.trigger_type,
            "priority": r.priority,
            "autonomy_level": r.autonomy_level,
            "created_at": r.created_at.isoformat()
        } for r in rules
    ]


@router.get("/rules/{rule_id}")
async def get_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get rule detail."""
    repo = AutonomyRepository(db)
    rule = await repo.get_rule(rule_id, current_user.id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return {
        "rule_id": rule.id,
        "name": rule.name,
        "goal_template": rule.goal_template,
        "enabled": rule.enabled,
        "trigger_type": rule.trigger_type,
        "priority": rule.priority,
        "autonomy_level": rule.autonomy_level,
        "created_at": rule.created_at.isoformat()
    }


@router.post("/rules/{rule_id}/enable")
async def enable_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enable autonomy rule."""
    repo = AutonomyRepository(db)
    rule = await repo.toggle_rule_enabled(rule_id, current_user.id, True)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return {"rule_id": rule_id, "enabled": True}


@router.post("/rules/{rule_id}/disable")
async def disable_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disable autonomy rule."""
    repo = AutonomyRepository(db)
    rule = await repo.toggle_rule_enabled(rule_id, current_user.id, False)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return {"rule_id": rule_id, "enabled": False}


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete autonomy rule."""
    repo = AutonomyRepository(db)
    success = await repo.delete_rule(rule_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return {"rule_id": rule_id, "deleted": True}


@router.post("/rules/{rule_id}/test")
async def test_rule_trigger(
    rule_id: str,
    req: TriggerTestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually test and trigger an autonomy rule."""
    manager = AutonomyManager(db)
    try:
        res = await manager.handle_trigger_event(
            user_id=current_user.id,
            rule_id=rule_id,
            event_type=req.event_type,
            source=req.source,
            payload=req.payload or {}
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/events")
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List event log."""
    repo = AutonomyRepository(db)
    events = await repo.list_events(current_user.id)
    return [
        {
            "event_id": e.id,
            "event_type": e.event_type,
            "source": e.source,
            "importance": e.importance,
            "created_at": e.created_at.isoformat()
        } for e in events
    ]


@router.get("/notifications")
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List notifications."""
    repo = AutonomyRepository(db)
    notifs = await repo.list_notifications(current_user.id)
    return [
        {
            "notification_id": n.id,
            "title": n.title,
            "summary": n.summary,
            "priority": n.priority,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        } for n in notifs
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read."""
    repo = AutonomyRepository(db)
    success = await repo.mark_notification_read(notification_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return {"notification_id": notification_id, "is_read": True}
