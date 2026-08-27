from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.connection import get_db
from app.database.models import AgentModel

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class AgentResponse(BaseModel):
    id: str
    name: str
    code_name: str
    description: str
    status: str


@router.get("/", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AgentModel))
    agents = result.scalars().all()
    return [
        AgentResponse(
            id=a.id,
            name=a.name,
            code_name=a.code_name,
            description=a.description or "",
            status=a.status
        )
        for a in agents
    ]
