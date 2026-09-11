import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.core.ultron_core import UltronCore
from app.core.capability_registry import CapabilityRegistry
from app.database.repositories.ultron_repo import UltronRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ultron", tags=["ultron"])


class CommandRequest(BaseModel):
    message: str = Field(..., description="User natural language command ('ULTRON, handle this')")
    workspace_id: Optional[str] = Field(default=None, description="Optional workspace ID")


@router.post("/command", status_code=status.HTTP_200_OK)
async def execute_command(
    req: CommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute unified user command converting natural language into an autonomous workflow DAG."""
    core = UltronCore(db)
    repo = UltronRepository(db)

    res = await core.execute_unified_command(
        user_id=current_user.id,
        message=req.message,
        workspace_id=req.workspace_id
    )

    cmd_model = await repo.create_command(
        user_id=current_user.id,
        raw_message=req.message,
        intent_type=res["intent"]["intent_type"],
        workflow_id=res["workflow_id"]
    )

    await repo.record_activity(
        user_id=current_user.id,
        activity_type="COMMAND_RECEIVED",
        title=f"Command Received: {req.message[:40]}",
        workflow_id=res["workflow_id"],
        details=f"Intent: {res['intent']['intent_type']}"
    )

    return {
        "command_id": cmd_model.id,
        "workflow_id": res["workflow_id"],
        "status": "RUNNING",
        "intent": res["intent"],
        "requires_approval": res["requires_approval"]
    }


@router.get("/status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get production system health, capability status, and operating mode."""
    cap_reg = CapabilityRegistry()
    health = cap_reg.get_system_health()
    from app.config.settings import settings
    from app.engine.redis_client import redis_client

    db_status = "healthy"
    try:
        from sqlalchemy.sql import text
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"

    return {
        "operating_system": f"PROJECT ULTRON OS v{settings.VERSION}",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "user_id": current_user.id,
        "system_status": health["status"],
        "database_health": db_status,
        "redis_health": "healthy" if redis_client.is_available else "degraded_in_memory",
        "worker_health": "healthy",
        "emergency_shutdown_active": settings.EMERGENCY_SHUTDOWN_ACTIVE,
        "total_capabilities": health["total_capabilities"],
        "available_capabilities": health["available_capabilities"],
        "capabilities": health["capabilities"]
    }


class EmergencyShutdownRequest(BaseModel):
    reason: str = Field(..., description="Reason for emergency shutdown invocation")


@router.post("/emergency-shutdown")
async def emergency_shutdown(
    req: EmergencyShutdownRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Emergency control mechanism: Safely disable autonomy triggers & integrations without destroying data."""
    from app.config.settings import settings
    settings.EMERGENCY_SHUTDOWN_ACTIVE = True
    repo = UltronRepository(db)
    await repo.record_activity(
        user_id=current_user.id,
        activity_type="EMERGENCY_SHUTDOWN_TRIGGERED",
        title="Emergency Control Activated",
        details=f"Reason: {req.reason} | Initiated by User: {current_user.id}"
    )
    logger.warning("EMERGENCY SHUTDOWN ACTIVATED by user %s. Reason: %s", current_user.id, req.reason)
    return {
        "status": "SHUTDOWN_ACTIVE",
        "emergency_shutdown_active": True,
        "message": "Autonomy engine, integrations, and new workflow dispatch disabled. Persistent data intact.",
        "reason": req.reason
    }


@router.get("/capabilities")
async def list_capabilities(
    current_user: User = Depends(get_current_user)
):
    """List system capabilities."""
    cap_reg = CapabilityRegistry()
    return [c.dict() for c in cap_reg.list_capabilities()]


@router.get("/timeline")
async def get_timeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get unified activity timeline."""
    repo = UltronRepository(db)
    activities = await repo.list_timeline(current_user.id)
    return [
        {
            "activity_id": a.id,
            "workflow_id": a.workflow_id,
            "activity_type": a.activity_type,
            "title": a.title,
            "details": a.details,
            "created_at": a.created_at.isoformat()
        } for a in activities
    ]
