import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.autonomy_repo import AutonomyRepository
from app.autonomy.event_bus import EventBus
from app.autonomy.decision_engine import ProactiveDecisionEngine
from app.autonomy.autonomy_executor import AutonomyExecutor
from app.autonomy.cooldown import CooldownManager
from app.autonomy.contracts import AutonomyLevel, PriorityLevel
from app.security.autonomy_security import AutonomySecurityValidator

logger = logging.getLogger("ULTRON.AutonomyManager")


class AutonomyManager:
    """Central Autonomy Manager orchestrating rules, triggers, events, decision engine, and workflow execution."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AutonomyRepository(db)
        self.event_bus = EventBus(db)
        self.decision_engine = ProactiveDecisionEngine(db)
        self.executor = AutonomyExecutor(db)

    async def create_rule(
        self,
        user_id: str,
        name: str,
        goal_template: str,
        trigger_type: str,
        trigger_config: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        priority: str = "MEDIUM",
        autonomy_level: str = "LEVEL_1",
        cooldown_seconds: int = 300
    ) -> Dict[str, Any]:
        rule = await self.repo.create_rule(
            user_id=user_id,
            name=name,
            goal_template=goal_template,
            trigger_type=trigger_type,
            trigger_config=trigger_config,
            description=description,
            priority=priority,
            autonomy_level=autonomy_level,
            cooldown_seconds=cooldown_seconds
        )
        return {
            "rule_id": rule.id,
            "name": rule.name,
            "enabled": rule.enabled,
            "trigger_type": rule.trigger_type,
            "autonomy_level": rule.autonomy_level,
            "created_at": rule.created_at.isoformat()
        }

    async def handle_trigger_event(
        self,
        user_id: str,
        rule_id: str,
        event_type: str,
        source: str,
        payload: Dict[str, Any],
        autonomy_level_override: Optional[str] = None
    ) -> Dict[str, Any]:
        rule = await self.repo.get_rule(rule_id, user_id)
        if not rule:
            raise ValueError(f"Autonomy rule '{rule_id}' not found for user '{user_id}'")

        if not rule.enabled:
            return {"status": "DISABLED", "rule_id": rule_id}

        if CooldownManager.is_in_cooldown(rule_id, rule.cooldown_seconds):
            return {"status": "COOLDOWN_ACTIVE", "rule_id": rule_id}

        CooldownManager.mark_executed(rule_id)

        # 1. Publish Event
        evt = await self.event_bus.publish_event(
            user_id=user_id,
            event_type=event_type,
            source=source,
            payload=payload,
            rule_id=rule_id,
            importance=rule.priority
        )

        if not evt:
            return {"status": "DEDUPLICATED", "rule_id": rule_id}

        # 2. Proactive Decision Engine Reasoning
        level_str = autonomy_level_override or rule.autonomy_level
        auto_level = AutonomyLevel(level_str)

        decision = await self.decision_engine.evaluate_event(
            event=evt,
            autonomy_level=auto_level,
            goal_template=rule.goal_template
        )

        # 3. Execute Decision
        exec_res = await self.executor.execute_decision(
            decision=decision,
            goal_template=rule.goal_template,
            rule_id=rule_id
        )

        await self.repo.update_rule_last_run(rule_id, user_id)

        return {
            "status": "PROCESSED",
            "rule_id": rule_id,
            "event_id": evt.event_id,
            "decision_id": decision.decision_id,
            "decision_type": decision.decision_type.value,
            "execution": exec_res
        }
