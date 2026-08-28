import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    UltronCommandModel,
    UltronCapabilityModel,
    UltronProjectContextModel,
    UltronResourceBudgetModel,
    UltronActivityTimelineModel
)

logger = logging.getLogger(__name__)


class UltronRepository:
    """Repository for Phase 10 Unified Personal Agent Operating System enforcing user_id tenant isolation."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # COMMANDS
    # -------------------------------------------------------------------------
    async def create_command(
        self,
        user_id: str,
        raw_message: str,
        intent_type: str,
        workflow_id: Optional[str] = None
    ) -> UltronCommandModel:
        cmd = UltronCommandModel(
            user_id=user_id,
            raw_message=raw_message,
            intent_type=intent_type,
            workflow_id=workflow_id,
            status="RECEIVED"
        )
        self.db.add(cmd)
        await self.db.commit()
        await self.db.refresh(cmd)
        return cmd

    async def update_command_status(
        self,
        command_id: str,
        user_id: str,
        status: str,
        workflow_id: Optional[str] = None,
        summary: Optional[str] = None
    ) -> Optional[UltronCommandModel]:
        stmt = select(UltronCommandModel).where(
            UltronCommandModel.id == command_id,
            UltronCommandModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        cmd = res.scalar_one_or_none()
        if cmd:
            cmd.status = status
            if workflow_id:
                cmd.workflow_id = workflow_id
            if summary:
                cmd.result_summary = summary
            if status in ("COMPLETED", "FAILED"):
                cmd.completed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(cmd)
        return cmd

    # -------------------------------------------------------------------------
    # CAPABILITIES & RESOURCE BUDGETS
    # -------------------------------------------------------------------------
    async def create_resource_budget(
        self,
        user_id: str,
        workflow_id: str,
        max_tool_calls: int = 50,
        max_runtime_seconds: int = 600,
        max_browser_steps: int = 20
    ) -> UltronResourceBudgetModel:
        budget = UltronResourceBudgetModel(
            user_id=user_id,
            workflow_id=workflow_id,
            max_tool_calls=max_tool_calls,
            max_runtime_seconds=max_runtime_seconds,
            max_browser_steps=max_browser_steps,
            status="ACTIVE"
        )
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget)
        return budget

    # -------------------------------------------------------------------------
    # ACTIVITY TIMELINE
    # -------------------------------------------------------------------------
    async def record_activity(
        self,
        user_id: str,
        activity_type: str,
        title: str,
        workflow_id: Optional[str] = None,
        details: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ) -> UltronActivityTimelineModel:
        act = UltronActivityTimelineModel(
            user_id=user_id,
            workflow_id=workflow_id,
            activity_type=activity_type,
            title=title,
            details=details,
            payload_json=payload or {}
        )
        self.db.add(act)
        await self.db.commit()
        await self.db.refresh(act)
        return act

    async def list_timeline(self, user_id: str, limit: int = 50) -> List[UltronActivityTimelineModel]:
        stmt = select(UltronActivityTimelineModel).where(
            UltronActivityTimelineModel.user_id == user_id
        ).order_by(UltronActivityTimelineModel.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
