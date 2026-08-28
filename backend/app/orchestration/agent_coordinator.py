import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.router import AgentRouter

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """Agent Coordinator delegating task execution to specialist agents."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.router = AgentRouter()

    async def execute_task(
        self,
        task_id: str,
        goal: str,
        assigned_agent: str,
        user_id: str,
        execution_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatch task to appropriate specialist agent via AgentRouter."""
        logger.info("AgentCoordinator dispatching task '%s' (%s) to agent '%s'", task_id, goal, assigned_agent)
        
        agent = self.router.get_agent(assigned_agent)
        if hasattr(agent, "execute"):
            try:
                res = await agent.execute(goal, str(context or {}))
            except TypeError:
                res = await agent.execute(goal)
            return {
                "task_id": task_id,
                "agent": assigned_agent,
                "status": "COMPLETED",
                "output": res
            }
        else:
            return {
                "task_id": task_id,
                "agent": assigned_agent,
                "status": "COMPLETED",
                "output": {"goal": goal, "assigned_agent": assigned_agent}
            }
