from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Conversation, Message


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_conversation(self, user_id: str, title: str = "New Conversation") -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation

    async def get_user_conversations(self, user_id: str) -> List[Conversation]:
        stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def add_message(
        self,
        conversation_id: str,
        sender_type: str,
        sender_name: str,
        content: str,
        metadata_json: Optional[Dict[str, Any]] = None
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_name=sender_name,
            content=content,
            metadata_json=metadata_json
        )
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message

    async def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
