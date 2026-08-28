from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User
from app.database.repositories.intelligence_repo import IntelligenceRepository
from app.intelligence.strategy_engine import StrategyEngine
from app.intelligence.agent_metrics import AgentMetricsEngine

router = APIRouter(tags=["Learning & Strategy Engine"])


@router.get("/api/v1/learning/events")
async def list_learning_events(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = IntelligenceRepository(db)
    events = await repo.get_user_learning_events(user_id=current_user.id, limit=limit)
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "execution_id": e.execution_id,
            "event_type": e.event_type,
            "observation": e.observation_json or {},
            "pattern_detected": e.pattern_detected,
            "action_taken": e.action_taken_json or {},
            "created_at": e.created_at.isoformat()
        }
        for e in events
    ]


@router.get("/api/v1/learning/strategies")
async def list_strategies(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    strategy_engine = StrategyEngine(db)
    return await strategy_engine.get_all_strategies(limit=limit)


@router.get("/api/v1/learning/metrics")
@router.get("/api/v1/agents/metrics")
async def list_agent_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    metrics_engine = AgentMetricsEngine(db)
    return await metrics_engine.get_all_metrics()
