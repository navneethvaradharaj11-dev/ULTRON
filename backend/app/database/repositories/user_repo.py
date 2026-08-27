from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User, SessionModel
from datetime import datetime


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create_user(self, username: str, email: str, password_hash: str) -> User:
        user = User(username=username, email=email, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def create_session(self, user_id: str, token_hash: str, expires_at: datetime) -> SessionModel:
        session = SessionModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session
