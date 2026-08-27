from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.memory_repo import MemoryRepository


class MemoryManager:
    """Central Memory Manager handling short-term, conversation, and long-term memories."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.memory_repo = MemoryRepository(db)
        self._short_term_context: Dict[str, Any] = {}

    def set_short_term(self, key: str, value: Any):
        self._short_term_context[key] = value

    def get_short_term(self, key: str, default: Any = None) -> Any:
        return self._short_term_context.get(key, default)

    async def get_conversation_history(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        messages = await self.conv_repo.get_conversation_messages(conversation_id, limit=limit)
        return [
            {
                "id": msg.id,
                "sender_type": msg.sender_type,
                "sender_name": msg.sender_name,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    async def save_message(self, conversation_id: str, sender_type: str, sender_name: str, content: str) -> Dict[str, Any]:
        msg = await self.conv_repo.add_message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_name=sender_name,
            content=content
        )
        return {"id": msg.id, "sender_type": msg.sender_type, "sender_name": msg.sender_name, "content": msg.content}

    async def add_long_term_memory(self, user_id: str, content: str, importance: int = 3) -> Dict[str, Any]:
        mem = await self.memory_repo.create_memory(
            user_id=user_id,
            content=content,
            memory_type="long_term",
            importance=importance
        )
        return {"id": mem.id, "content": mem.content, "importance": mem.importance}

    async def get_long_term_memories(self, user_id: str) -> List[Dict[str, Any]]:
        mems = await self.memory_repo.get_user_memories(user_id, memory_type="long_term")
        return [{"id": m.id, "content": m.content, "importance": m.importance, "memory_type": m.memory_type} for m in mems]
