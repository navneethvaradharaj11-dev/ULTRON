from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import (
    BrowserSessionModel, BrowserActionModel, BrowserPageModel, ResearchSourceModel
)


class BrowserRepository:
    """Repository handling database operations for browser sessions, actions, pages, and research sources."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        execution_id: Optional[str] = None,
        current_url: Optional[str] = None
    ) -> BrowserSessionModel:
        session_record = BrowserSessionModel(
            id=session_id,
            user_id=user_id,
            execution_id=execution_id,
            current_url=current_url,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
        self.db.add(session_record)
        await self.db.commit()
        await self.db.refresh(session_record)
        return session_record

    async def get_session(self, session_id: str) -> Optional[BrowserSessionModel]:
        stmt = select(BrowserSessionModel).where(BrowserSessionModel.id == session_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_user_sessions(self, user_id: str) -> List[BrowserSessionModel]:
        stmt = select(BrowserSessionModel).where(BrowserSessionModel.user_id == user_id).order_by(BrowserSessionModel.created_at.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_session_url(self, session_id: str, current_url: str) -> Optional[BrowserSessionModel]:
        session_record = await self.get_session(session_id)
        if session_record:
            session_record.current_url = current_url
            await self.db.commit()
            await self.db.refresh(session_record)
        return session_record

    async def close_session(self, session_id: str) -> Optional[BrowserSessionModel]:
        session_record = await self.get_session(session_id)
        if session_record and session_record.status == "ACTIVE":
            session_record.status = "CLOSED"
            session_record.closed_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(session_record)
        return session_record

    async def log_action(
        self,
        action_id: str,
        session_id: str,
        action_type: str,
        params_json: Optional[Dict[str, Any]] = None,
        result_json: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS"
    ) -> BrowserActionModel:
        action_record = BrowserActionModel(
            id=action_id,
            session_id=session_id,
            action_type=action_type,
            params_json=params_json,
            result_json=result_json,
            status=status,
            created_at=datetime.utcnow()
        )
        self.db.add(action_record)
        await self.db.commit()
        await self.db.refresh(action_record)
        return action_record

    async def save_page_snapshot(
        self,
        page_id: str,
        session_id: str,
        url: str,
        title: Optional[str] = None,
        page_structure_json: Optional[Dict[str, Any]] = None
    ) -> BrowserPageModel:
        page_record = BrowserPageModel(
            id=page_id,
            session_id=session_id,
            url=url,
            title=title,
            page_structure_json=page_structure_json,
            captured_at=datetime.utcnow()
        )
        self.db.add(page_record)
        await self.db.commit()
        await self.db.refresh(page_record)
        return page_record

    async def save_research_source(
        self,
        source_pk: str,
        execution_id: str,
        source_id: str,
        url: str,
        title: Optional[str] = None,
        domain: Optional[str] = None,
        summary_json: Optional[Dict[str, Any]] = None
    ) -> ResearchSourceModel:
        source_record = ResearchSourceModel(
            id=source_pk,
            execution_id=execution_id,
            source_id=source_id,
            url=url,
            title=title,
            domain=domain,
            summary_json=summary_json,
            retrieved_at=datetime.utcnow()
        )
        self.db.add(source_record)
        await self.db.commit()
        await self.db.refresh(source_record)
        return source_record

    async def get_execution_sources(self, execution_id: str) -> List[ResearchSourceModel]:
        stmt = select(ResearchSourceModel).where(ResearchSourceModel.execution_id == execution_id).order_by(ResearchSourceModel.retrieved_at.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
