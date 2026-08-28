import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository

logger = logging.getLogger("ULTRON.StrategyEngine")


class StrategyEngine:
    """Manages workflow strategies, historical success rates, and optimal strategy selection."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IntelligenceRepository(db)

    async def best_strategy(self, goal_type: str) -> Optional[Dict[str, Any]]:
        """Query highest-ranked workflow strategy for given goal_type."""
        strats = await self.repo.get_strategies_by_goal_type(goal_type, limit=1)
        if not strats:
            return None
        s = strats[0]
        return self.to_dict(s)

    async def get_all_strategies(self, limit: int = 50) -> List[Dict[str, Any]]:
        strats = await self.repo.get_all_strategies(limit=limit)
        return [self.to_dict(s) for s in strats]

    async def record_strategy_execution(
        self,
        goal_type: str,
        description: str,
        steps: List[Dict[str, Any]],
        agents: List[str],
        tools: List[str],
        success: bool,
        duration_ms: int
    ) -> Dict[str, Any]:
        """Update or create strategy in library based on execution outcome."""
        strat = await self.repo.upsert_strategy(
            goal_type=goal_type,
            description=description,
            steps=steps,
            agents=agents,
            tools=tools,
            success=success,
            duration_ms=duration_ms
        )
        logger.info("Recorded strategy outcome for '%s' (success=%s, rate=%.2f)",
                    goal_type, success, strat.success_rate)
        return self.to_dict(strat)

    @staticmethod
    def to_dict(strat) -> Dict[str, Any]:
        return {
            "strategy_id": strat.id,
            "goal_type": strat.goal_type,
            "description": strat.description or "",
            "steps": strat.steps_json or [],
            "agents": strat.agents_json or [],
            "tools": strat.tools_json or [],
            "success_rate": strat.success_rate,
            "sample_count": strat.sample_count,
            "average_duration": strat.average_duration_ms,
            "failure_rate": strat.failure_rate,
            "confidence": strat.confidence,
            "updated_at": strat.updated_at.isoformat() if strat.updated_at else None
        }
