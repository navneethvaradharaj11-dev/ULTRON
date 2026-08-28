import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository

logger = logging.getLogger("ULTRON.AgentMetricsEngine")

SYSTEM_AGENTS = [
    "commander", "planner", "researcher", "coder",
    "reviewer", "browser_agent", "computer_agent", "learning_agent"
]


class AgentMetricsEngine:
    """Tracks and computes agent performance metrics across executions."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IntelligenceRepository(db)

    async def record_agent_run(
        self,
        agent_name: str,
        success: bool,
        duration_ms: int,
        retries: int = 0,
        tools_used: Optional[List[str]] = None,
        review_score: float = 1.0
    ) -> Dict[str, Any]:
        metric = await self.repo.update_agent_metrics(
            agent_name=agent_name.lower(),
            success=success,
            duration_ms=duration_ms,
            retries=retries,
            tools_used=tools_used,
            review_score=review_score
        )
        return self.to_dict(metric)

    async def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, Any]]:
        metrics = await self.get_all_metrics()
        for m in metrics:
            if m["agent_name"] == agent_name.lower():
                return m
        return None

    async def get_all_metrics(self) -> List[Dict[str, Any]]:
        db_metrics = await self.repo.get_all_agent_metrics()
        existing_names = {m.agent_name for m in db_metrics}

        result = [self.to_dict(m) for m in db_metrics]
        
        # Default entry for agents not yet in DB
        for sys_agent in SYSTEM_AGENTS:
            if sys_agent not in existing_names:
                result.append({
                    "agent_name": sys_agent,
                    "total_runs": 0,
                    "successful_runs": 0,
                    "failed_runs": 0,
                    "success_rate": 1.0,
                    "failure_rate": 0.0,
                    "average_duration": 0,
                    "retry_count": 0,
                    "tool_usage": {},
                    "review_score": 1.0
                })
        return result

    @staticmethod
    def to_dict(metric) -> Dict[str, Any]:
        total = metric.total_runs or 1
        succ_rate = round(metric.successful_runs / total, 2)
        fail_rate = round(metric.failed_runs / total, 2)

        return {
            "agent_name": metric.agent_name,
            "total_runs": metric.total_runs,
            "successful_runs": metric.successful_runs,
            "failed_runs": metric.failed_runs,
            "success_rate": succ_rate,
            "failure_rate": fail_rate,
            "average_duration": metric.average_duration_ms,
            "retry_count": metric.total_retries,
            "tool_usage": metric.tools_usage_json or {},
            "review_score": metric.average_review_score
        }
