import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository

logger = logging.getLogger("ULTRON.FeedbackEngine")


class FeedbackEngine:
    """Captures explicit user execution feedback, ratings, and output corrections."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IntelligenceRepository(db)

    async def submit_feedback(
        self,
        user_id: str,
        execution_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        corrected_output: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record user feedback and log learning event."""
        fb = await self.repo.record_feedback(
            user_id=user_id,
            execution_id=execution_id,
            rating=rating,
            feedback_text=feedback_text,
            corrected_output=corrected_output
        )

        # Log learning event for user feedback
        await self.repo.record_learning_event(
            user_id=user_id,
            execution_id=execution_id,
            event_type="USER_FEEDBACK",
            observation={"rating": rating, "feedback_text": feedback_text},
            pattern_detected="Explicit User Evaluation",
            action_taken={"action": "update_learning_weights"}
        )

        logger.info("Recorded user feedback for execution '%s' (rating=%d)", execution_id, rating)
        return {
            "id": fb.id,
            "user_id": fb.user_id,
            "execution_id": fb.execution_id,
            "rating": fb.rating,
            "feedback_text": fb.feedback_text,
            "created_at": fb.created_at.isoformat()
        }
