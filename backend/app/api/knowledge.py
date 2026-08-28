import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.knowledge.knowledge_engine import KnowledgeEngine
from app.database.repositories.knowledge_repo import KnowledgeRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(..., description="Workspace name")
    description: Optional[str] = Field(default=None, description="Workspace description")


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    workspace_id: Optional[str] = Field(default=None, description="Optional workspace filter")
    top_k: int = Field(default=5, description="Number of results to return")


@router.post("/workspaces", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    req: CreateWorkspaceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge workspace."""
    engine = KnowledgeEngine(db)
    return await engine.create_workspace(user_id=current_user.id, name=req.name, description=req.description)


@router.get("/workspaces")
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List workspaces for authenticated user."""
    engine = KnowledgeEngine(db)
    return await engine.list_workspaces(user_id=current_user.id)


@router.get("/workspaces/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workspace detail and knowledge graph."""
    repo = KnowledgeRepository(db)
    ws = await repo.get_workspace(workspace_id, current_user.id)
    if not ws:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    engine = KnowledgeEngine(db)
    graph = await engine.get_workspace_graph(current_user.id, workspace_id)
    return {
        "workspace_id": ws.id,
        "name": ws.name,
        "description": ws.description,
        "graph": graph,
        "created_at": ws.created_at.isoformat()
    }


@router.post("/sources/upload", status_code=status.HTTP_201_CREATED)
async def upload_source_file(
    workspace_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and ingest a file source into workspace."""
    content_bytes = await file.read()
    engine = KnowledgeEngine(db)
    try:
        res = await engine.upload_and_ingest_source(
            user_id=current_user.id,
            workspace_id=workspace_id,
            filename=file.filename or "file",
            content_bytes=content_bytes,
            mime_type=file.content_type or "application/octet-stream"
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sources")
async def list_sources(
    workspace_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List knowledge sources."""
    repo = KnowledgeRepository(db)
    sources = await repo.list_sources(user_id=current_user.id, workspace_id=workspace_id)
    return [
        {
            "source_id": s.id,
            "filename": s.filename,
            "source_type": s.source_type,
            "size_bytes": s.size_bytes,
            "status": s.status,
            "created_at": s.created_at.isoformat()
        } for s in sources
    ]


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete source and perform cleanup."""
    engine = KnowledgeEngine(db)
    success = await engine.delete_source(source_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return {"source_id": source_id, "deleted": True}


@router.post("/search")
async def search_knowledge(
    req: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute hybrid search and return evidence package with citations."""
    engine = KnowledgeEngine(db)
    return await engine.query_knowledge(
        user_id=current_user.id,
        query=req.query,
        workspace_id=req.workspace_id,
        top_k=req.top_k
    )
