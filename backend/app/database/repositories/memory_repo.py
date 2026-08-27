from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Memory


class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "long_term",
        importance: int = 1,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> Memory:
        memory = Memory(
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            metadata_json=metadata_json
        )
        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)
        return memory

    async def get_user_memories(self, user_id: str, memory_type: Optional[str] = None) -> List[Memory]:
        stmt = select(Memory).where(Memory.user_id == user_id)
        if memory_type:
            stmt = stmt.where(Memory.memory_type == memory_type)
        stmt = stmt.order_by(Memory.importance.desc(), Memory.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        stmt = select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        result = await self.session.execute(stmt)
        memory = result.scalars().first()
        if memory:
            await self.session.delete(memory)
            await self.session.commit()
            return True
        return False
