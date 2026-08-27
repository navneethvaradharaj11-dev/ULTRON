from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.conversation_repo import ConversationRepository

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    status: str
    created_at: str


class MessageResponse(BaseModel):
    id: str
    sender_type: str
    sender_name: str
    content: str
    created_at: str


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    req: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.create_conversation(user_id=current_user.id, title=req.title or "New Conversation")
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        title=conv.title,
        status=conv.status,
        created_at=conv.created_at.isoformat()
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    convs = await repo.get_user_conversations(current_user.id)
    return [
        ConversationResponse(
            id=c.id,
            user_id=c.user_id,
            title=c.title,
            status=c.status,
            created_at=c.created_at.isoformat()
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = ConversationRepository(db)
    conv = await repo.get_by_id(conversation_id)
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await repo.get_conversation_messages(conversation_id)
    return [
        MessageResponse(
            id=m.id,
            sender_type=m.sender_type,
            sender_name=m.sender_name,
            content=m.content,
            created_at=m.created_at.isoformat()
        )
        for m in messages
    ]
