import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    AutonomyRuleModel,
    AutonomyTriggerModel,
    AutonomyEventModel,
    AutonomyDecisionModel,
    AutonomyExecutionModel,
    AutonomyNotificationModel,
    AutonomyMonitorStateModel
)

logger = logging.getLogger(__name__)


class AutonomyRepository:
    """Repository enforcing multi-tenant user_id ownership for Phase 9 Autonomy Engine."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # RULES
    # -------------------------------------------------------------------------
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
        cooldown_seconds: int = 300,
        max_runs_per_hour: int = 10
    ) -> AutonomyRuleModel:
        rule = AutonomyRuleModel(
            user_id=user_id,
            name=name,
            goal_template=goal_template,
            trigger_type=trigger_type,
            trigger_config_json=trigger_config or {},
            description=description,
            priority=priority,
            autonomy_level=autonomy_level,
            cooldown_seconds=cooldown_seconds,
            max_runs_per_hour=max_runs_per_hour,
            enabled=True
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_rule(self, rule_id: str, user_id: str) -> Optional[AutonomyRuleModel]:
        stmt = select(AutonomyRuleModel).where(
            AutonomyRuleModel.id == rule_id,
            AutonomyRuleModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_rules(self, user_id: str, enabled_only: bool = False) -> List[AutonomyRuleModel]:
        stmt = select(AutonomyRuleModel).where(AutonomyRuleModel.user_id == user_id)
        if enabled_only:
            stmt = stmt.where(AutonomyRuleModel.enabled == True)
        stmt = stmt.order_by(AutonomyRuleModel.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def toggle_rule_enabled(self, rule_id: str, user_id: str, enabled: bool) -> Optional[AutonomyRuleModel]:
        rule = await self.get_rule(rule_id, user_id)
        if rule:
            rule.enabled = enabled
            rule.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(rule)
        return rule

    async def update_rule_last_run(self, rule_id: str, user_id: str) -> None:
        rule = await self.get_rule(rule_id, user_id)
        if rule:
            rule.last_run_at = datetime.utcnow()
            await self.db.commit()

    async def delete_rule(self, rule_id: str, user_id: str) -> bool:
        stmt = delete(AutonomyRuleModel).where(
            AutonomyRuleModel.id == rule_id,
            AutonomyRuleModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    # -------------------------------------------------------------------------
    # EVENTS & DECISIONS
    # -------------------------------------------------------------------------
    async def create_event(
        self,
        user_id: str,
        event_type: str,
        source: str,
        deduplication_key: str,
        rule_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        importance: str = "MEDIUM"
    ) -> AutonomyEventModel:
        evt = AutonomyEventModel(
            user_id=user_id,
            rule_id=rule_id,
            event_type=event_type,
            source=source,
            deduplication_key=deduplication_key,
            payload_json=payload or {},
            importance=importance
        )
        self.db.add(evt)
        await self.db.commit()
        await self.db.refresh(evt)
        return evt

    async def list_events(self, user_id: str, limit: int = 50) -> List[AutonomyEventModel]:
        stmt = select(AutonomyEventModel).where(
            AutonomyEventModel.user_id == user_id
        ).order_by(AutonomyEventModel.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def create_decision(
        self,
        event_id: str,
        user_id: str,
        decision_type: str,
        reasoning: str,
        rule_id: Optional[str] = None,
        confidence: float = 1.0,
        priority: str = "MEDIUM",
        evidence: Optional[Dict[str, Any]] = None
    ) -> AutonomyDecisionModel:
        dec = AutonomyDecisionModel(
            event_id=event_id,
            user_id=user_id,
            rule_id=rule_id,
            decision_type=decision_type,
            reasoning=reasoning,
            confidence=confidence,
            priority=priority,
            evidence_json=evidence or {}
        )
        self.db.add(dec)
        await self.db.commit()
        await self.db.refresh(dec)
        return dec

    # -------------------------------------------------------------------------
    # NOTIFICATIONS
    # -------------------------------------------------------------------------
    async def create_notification(
        self,
        user_id: str,
        title: str,
        summary: str,
        priority: str = "MEDIUM",
        rule_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> AutonomyNotificationModel:
        notif = AutonomyNotificationModel(
            user_id=user_id,
            rule_id=rule_id,
            title=title,
            summary=summary,
            priority=priority,
            is_read=False,
            payload_json=payload or {}
        )
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def list_notifications(self, user_id: str, limit: int = 50) -> List[AutonomyNotificationModel]:
        stmt = select(AutonomyNotificationModel).where(
            AutonomyNotificationModel.user_id == user_id
        ).order_by(AutonomyNotificationModel.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        stmt = select(AutonomyNotificationModel).where(
            AutonomyNotificationModel.id == notification_id,
            AutonomyNotificationModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        notif = res.scalar_one_or_none()
        if notif:
            notif.is_read = True
            await self.db.commit()
            return True
        return False
