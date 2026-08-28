from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.memory_retriever import MemoryRetriever
from app.intelligence.memory_consolidator import MemoryConsolidator

router = APIRouter(prefix="/api/v1/memory", tags=["Memory Engine"])


class CreateMemoryRequest(BaseModel):
    content: str = Field(..., description="Memory text content")
    type: str = Field(default="SEMANTIC", description="Category: WORKING, EPISODIC, SEMANTIC, PROCEDURAL, PREFERENCE")
    importance: int = Field(default=1, ge=1, le=5)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = Field(default="user_explicit")
    metadata: Optional[Dict[str, Any]] = None


class SearchMemoryRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    top_k: int = Field(default=5, ge=1, le=50)
    type: Optional[str] = None


class ConsolidateMemoryRequest(BaseModel):
    observations: List[Dict[str, Any]] = Field(..., description="List of short-term observations")
    category: str = Field(default="SEMANTIC")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_memory(
    req: CreateMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = MemoryEngine(db)
    try:
        mem = await engine.add_memory(
            user_id=current_user.id,
            content=req.content,
            memory_type=req.type,
            importance=req.importance,
            confidence=req.confidence,
            source=req.source,
            metadata=req.metadata
        )
        return mem
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_memories(
    type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = MemoryEngine(db)
    return await engine.list_memories(user_id=current_user.id, memory_type=type, limit=limit)


@router.get("/{memory_id}")
async def get_memory_by_id(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = MemoryEngine(db)
    mem = await engine.get_memory(memory_id=memory_id, user_id=current_user.id)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found or access denied.")
    return mem


@router.post("/search")
async def search_memories(
    req: SearchMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    retriever = MemoryRetriever(db)
    return await retriever.search_memories(user_id=current_user.id, query=req.query, limit=req.top_k)


@router.post("/semantic-search")
async def semantic_search_memories(
    req: SearchMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    retriever = MemoryRetriever(db)
    return await retriever.retrieve_relevant_memories(
        user_id=current_user.id,
        user_request=req.query,
        top_k=req.top_k,
        memory_type=req.type
    )


@router.post("/consolidate")
async def consolidate_memories(
    req: ConsolidateMemoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    consolidator = MemoryConsolidator(db)
    res = await consolidator.consolidate_observations(
        user_id=current_user.id,
        observations=req.observations,
        category=req.category
    )
    return res


@router.post("/{memory_id}/forget")
async def forget_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = MemoryEngine(db)
    success = await engine.forget_memory(memory_id=memory_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or access denied.")
    return {"status": "FORGOTTEN", "id": memory_id}


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    engine = MemoryEngine(db)
    success = await engine.delete_memory(memory_id=memory_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found or access denied.")
    return {"status": "DELETED", "id": memory_id}
