from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.memory_repo import MemoryRepository

router = APIRouter(prefix="/api/v1/memory", tags=["Memory"])


class MemoryCreateRequest(BaseModel):
    content: str
    memory_type: str = "long_term"
    importance: int = 3


class MemoryResponse(BaseModel):
    id: str
    content: str
    memory_type: str
    importance: int
    created_at: str


@router.post("/", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def add_memory(
    req: MemoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MemoryRepository(db)
    mem = await repo.create_memory(
        user_id=current_user.id,
        content=req.content,
        memory_type=req.memory_type,
        importance=req.importance
    )
    return MemoryResponse(
        id=mem.id,
        content=mem.content,
        memory_type=mem.memory_type,
        importance=mem.importance,
        created_at=mem.created_at.isoformat()
    )


@router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MemoryRepository(db)
    mems = await repo.get_user_memories(current_user.id)
    return [
        MemoryResponse(
            id=m.id,
            content=m.content,
            memory_type=m.memory_type,
            importance=m.importance,
            created_at=m.created_at.isoformat()
        )
        for m in mems
    ]


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = MemoryRepository(db)
    success = await repo.delete_memory(memory_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
