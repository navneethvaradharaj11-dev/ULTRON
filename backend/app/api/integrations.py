import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.integrations.contracts import IntegrationExecutionRequest
from app.integrations.integration_registry import integration_registry
from app.integrations.integration_manager import IntegrationManager
from app.integrations.health_manager import health_manager
from app.integrations.github.adapter import GitHubAdapter
from app.integrations.calendar.adapter import CalendarAdapter
from app.integrations.email.adapter import EmailAdapter
from app.integrations.filesystem.adapter import FilesystemAdapter
from app.database.repositories.integration_repo import IntegrationRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

# Initialize default adapters
_github = GitHubAdapter()
_calendar = CalendarAdapter()
_email = EmailAdapter()
_filesystem = FilesystemAdapter()

_manager = IntegrationManager(adapters={
    "github": _github,
    "calendar": _calendar,
    "email": _email,
    "filesystem": _filesystem
})


class ExecuteRequest(BaseModel):
    integration_id: str
    operation_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    workflow_id: Optional[str] = None


@router.get("", status_code=status.HTTP_200_OK)
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all registered integrations and active connections."""
    repo = IntegrationRepository(db)
    conns = await repo.list_connections(current_user.id)
    connected_ids = {c.integration_id for c in conns}

    items = []
    for desc in integration_registry.list_all():
        items.append({
            "id": desc.id,
            "name": desc.name,
            "provider": desc.provider,
            "version": desc.version,
            "description": desc.description,
            "risk_level": desc.risk_level,
            "health_status": health_manager.get_status(desc.id),
            "is_connected": desc.id in connected_ids,
            "capabilities": desc.capabilities
        })
    return items


@router.get("/{id}")
async def get_integration(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """Get integration details by ID."""
    desc = integration_registry.get(id)
    if not desc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Integration '{id}' not found")
    return desc.dict()


@router.get("/{id}/health")
async def get_health(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """Get health status for a specific integration."""
    if not integration_registry.has(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Integration '{id}' not found")
    return {"integration_id": id, "health_status": health_manager.get_status(id)}


@router.get("/{id}/operations")
async def get_operations(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """List supported operations for an integration."""
    desc = integration_registry.get(id)
    if not desc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Integration '{id}' not found")
    return {op_id: op.dict() for op_id, op in desc.supported_operations.items()}


@router.post("/{id}/connect", status_code=status.HTTP_200_OK)
async def connect_integration(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect integration for current user."""
    if not integration_registry.has(id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Integration '{id}' not found")
    repo = IntegrationRepository(db)
    conn = await repo.create_connection(current_user.id, id.lower())
    health_manager.set_status(id, "CONNECTED")
    return {"connected": True, "connection_id": conn.id, "integration_id": id}


@router.post("/{id}/disconnect", status_code=status.HTTP_200_OK)
async def disconnect_integration(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect integration for current user."""
    repo = IntegrationRepository(db)
    ok = await repo.disconnect(current_user.id, id.lower())
    health_manager.set_status(id, "DISCONNECTED")
    return {"disconnected": ok, "integration_id": id}


@router.post("/execute")
async def execute_integration_operation(
    req: ExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an integration operation."""
    exec_req = IntegrationExecutionRequest(
        user_id=current_user.id,
        integration_id=req.integration_id,
        operation_id=req.operation_id,
        parameters=req.parameters,
        workflow_id=req.workflow_id
    )

    res = await _manager.execute_operation(exec_req)
    repo = IntegrationRepository(db)
    await repo.record_audit_log(
        user_id=current_user.id,
        integration_id=req.integration_id,
        operation_id=req.operation_id,
        status=res.status,
        duration_ms=res.duration_ms,
        details=res.error_message
    )

    return res.dict()


@router.get("/events")
async def get_integration_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get audit events for integrations."""
    repo = IntegrationRepository(db)
    logs = await repo.list_audit_logs(current_user.id)
    return [
        {
            "id": l.id,
            "integration_id": l.integration_id,
            "operation_id": l.operation_id,
            "status": l.status,
            "duration_ms": l.duration_ms,
            "created_at": l.created_at.isoformat()
        } for l in logs
    ]
