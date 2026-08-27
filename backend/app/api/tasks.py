from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.task_repo import TaskRepository

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"])


class TaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"


class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    created_at: str


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    req: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.create_task(
        user_id=current_user.id,
        title=req.title,
        description=req.description,
        priority=req.priority
    )
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        created_at=task.created_at.isoformat()
    )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    tasks = await repo.get_user_tasks(current_user.id)
    return [
        TaskResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            created_at=t.created_at.isoformat()
        )
        for t in tasks
    ]


@router.patch("/{task_id}/status", response_model=TaskResponse)
async def update_status(
    task_id: str,
    status_val: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    updated = await repo.update_task_status(task_id, current_user.id, status_val)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(
        id=updated.id,
        title=updated.title,
        description=updated.description,
        status=updated.status,
        priority=updated.priority,
        created_at=updated.created_at.isoformat()
    )
