import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import (
    ComputerSessionModel, ComputerScreenshotModel, PerceptionResultModel, ComputerActionModel
)


class ComputerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------------------------------------------------------
    # Computer Session CRUD
    # ------------------------------------------------------------------

    async def create_session(
        self,
        user_id: str,
        execution_id: str,
        viewport_width: int = 1280,
        viewport_height: int = 800
    ) -> ComputerSessionModel:
        sess = ComputerSessionModel(
            user_id=user_id,
            execution_id=execution_id,
            status="ACTIVE",
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            started_at=datetime.utcnow()
        )
        self.session.add(sess)
        await self.session.commit()
        await self.session.refresh(sess)
        return sess

    async def get_session(self, session_id: str) -> Optional[ComputerSessionModel]:
        stmt = select(ComputerSessionModel).where(ComputerSessionModel.id == session_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_user_sessions(self, user_id: str) -> List[ComputerSessionModel]:
        stmt = (
            select(ComputerSessionModel)
            .where(ComputerSessionModel.user_id == user_id)
            .order_by(ComputerSessionModel.started_at.desc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def close_session(self, session_id: str) -> Optional[ComputerSessionModel]:
        sess = await self.get_session(session_id)
        if sess:
            sess.status = "CLOSED"
            sess.ended_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(sess)
        return sess

    # ------------------------------------------------------------------
    # Computer Screenshots CRUD
    # ------------------------------------------------------------------

    async def save_screenshot(
        self,
        session_id: str,
        execution_id: str,
        image_metadata: Optional[Dict[str, Any]] = None,
        width: int = 1280,
        height: int = 800
    ) -> ComputerScreenshotModel:
        shot = ComputerScreenshotModel(
            session_id=session_id,
            execution_id=execution_id,
            image_metadata=image_metadata or {},
            width=width,
            height=height,
            created_at=datetime.utcnow()
        )
        self.session.add(shot)
        await self.session.commit()
        await self.session.refresh(shot)
        return shot

    async def get_screenshot(self, screenshot_id: str) -> Optional[ComputerScreenshotModel]:
        stmt = select(ComputerScreenshotModel).where(ComputerScreenshotModel.id == screenshot_id)
        res = await self.session.execute(stmt)
        return res.scalars().first()

    # ------------------------------------------------------------------
    # Perception Results CRUD
    # ------------------------------------------------------------------

    async def save_perception_result(
        self,
        screenshot_id: str,
        execution_id: str,
        result_json: Dict[str, Any],
        confidence: float = 0.0
    ) -> PerceptionResultModel:
        pr = PerceptionResultModel(
            screenshot_id=screenshot_id,
            execution_id=execution_id,
            result_json=result_json,
            confidence=confidence,
            created_at=datetime.utcnow()
        )
        self.session.add(pr)
        await self.session.commit()
        await self.session.refresh(pr)
        return pr

    # ------------------------------------------------------------------
    # Computer Actions CRUD
    # ------------------------------------------------------------------

    async def create_action(
        self,
        session_id: str,
        execution_id: str,
        action_type: str,
        target_json: Optional[Dict[str, Any]] = None,
        parameters_json: Optional[Dict[str, Any]] = None,
        approval_state: str = "AUTO_APPROVED",
        confidence: float = 1.0
    ) -> ComputerActionModel:
        act = ComputerActionModel(
            session_id=session_id,
            execution_id=execution_id,
            action_type=action_type,
            target_json=target_json or {},
            parameters_json=parameters_json or {},
            status="PENDING",
            approval_state=approval_state,
            confidence=confidence,
            created_at=datetime.utcnow()
        )
        self.session.add(act)
        await self.session.commit()
        await self.session.refresh(act)
        return act

    async def update_action_status(
        self,
        action_id: str,
        status: str,
        result_json: Optional[Dict[str, Any]] = None
    ) -> Optional[ComputerActionModel]:
        stmt = select(ComputerActionModel).where(ComputerActionModel.id == action_id)
        res = await self.session.execute(stmt)
        act = res.scalars().first()
        if act:
            act.status = status
            if result_json is not None:
                act.result_json = result_json
            if status in ("COMPLETED", "FAILED", "REJECTED", "CANCELLED"):
                act.completed_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(act)
        return act

    async def get_session_actions(self, session_id: str) -> List[ComputerActionModel]:
        stmt = (
            select(ComputerActionModel)
            .where(ComputerActionModel.session_id == session_id)
            .order_by(ComputerActionModel.created_at.asc())
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
