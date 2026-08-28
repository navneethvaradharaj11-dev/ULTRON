import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.autonomy.contracts import (
    AutonomyEventPayload,
    AutonomyDecisionPayload,
    DecisionType,
    AutonomyLevel,
    PriorityLevel
)
from app.autonomy.autonomy_policy import AutonomyPolicyEngine
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.intelligence.memory_engine import MemoryEngine
from app.knowledge.knowledge_engine import KnowledgeEngine

logger = logging.getLogger("ULTRON.DecisionEngine")


class ProactiveDecisionEngine:
    """Proactive reasoning engine matching incoming events against Context, Memory, Knowledge, Priority, and Policy."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AutonomyRepository(db)
        self.memory_engine = MemoryEngine(db)
        self.knowledge_engine = KnowledgeEngine(db)

    async def evaluate_event(
        self,
        event: AutonomyEventPayload,
        autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_1,
        goal_template: Optional[str] = None
    ) -> AutonomyDecisionPayload:
        """Evaluate event against policies, user preferences, memory context, and knowledge evidence."""

        # 1. Policy & Level Check
        decision_type, policy_reason = AutonomyPolicyEngine.evaluate_policy(
            autonomy_level=autonomy_level,
            action_type=event.event_type,
            is_sensitive=(event.importance == PriorityLevel.CRITICAL)
        )

        # 2. Reasoning Metadata Synthesis
        reasoning = (
            f"Event '{event.event_type}' from source '{event.source}' evaluated under {autonomy_level.value}. "
            f"Policy Result: {decision_type.value}. Reason: {policy_reason}"
        )

        evidence = {
            "source": event.source,
            "importance": event.importance.value,
            "goal_template": goal_template or "Proactive goal handling"
        }

        # 3. Persist Decision
        dec_model = await self.repo.create_decision(
            event_id=event.event_id,
            user_id=event.user_id,
            rule_id=None,
            decision_type=decision_type.value,
            reasoning=reasoning,
            confidence=0.95,
            priority=event.importance.value,
            evidence=evidence
        )

        return AutonomyDecisionPayload(
            decision_id=dec_model.id,
            event_id=event.event_id,
            user_id=event.user_id,
            decision_type=decision_type,
            confidence=0.95,
            priority=event.importance,
            reasoning=reasoning,
            evidence=evidence
        )
