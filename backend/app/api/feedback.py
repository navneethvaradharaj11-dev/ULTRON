import logging
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User

logger = logging.getLogger("ULTRON.API.Feedback")

router = APIRouter(prefix="/api/v1/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    category: str = Field(..., description="BUG, FEATURE_REQUEST, CONFUSING_RESULT, WRONG_ANSWER, PERFORMANCE_ISSUE, SECURITY_CONCERN")
    description: str = Field(..., min_length=5, description="Detailed feedback or bug report description")
    correlation_id: Optional[str] = Field(None, description="Optional request or workflow correlation ID")


class FeedbackResponse(BaseModel):
    ticket_id: str
    status: str
    message: str


@router.post("", status_code=status.HTTP_201_CREATED, response_model=FeedbackResponse)
async def submit_user_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit user feedback or bug report with optional correlation tracing."""
    ticket_id = f"fbk-{uuid.uuid4().hex[:8]}"
    logger.info(
        "Feedback ticket '%s' created by user '%s' [category=%s, correlation_id=%s]",
        ticket_id, current_user.username, request.category, request.correlation_id or "none"
    )
    return FeedbackResponse(
        ticket_id=ticket_id,
        status="RECEIVED",
        message="Thank you for your feedback. Our operations team will investigate using the provided correlation trace."
    )
