from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Task


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        conversation_id: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None
    ) -> Task:
        task = Task(
            user_id=user_id,
            conversation_id=conversation_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_user_tasks(self, user_id: str) -> List[Task]:
        stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_task_status(self, task_id: str, user_id: str, status: str) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await self.session.execute(stmt)
        task = result.scalars().first()
        if task:
            task.status = status
            await self.session.commit()
            await self.session.refresh(task)
        return task
