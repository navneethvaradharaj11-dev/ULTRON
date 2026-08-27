import logging
from typing import Dict, Any, Optional
from app.ai.model_manager import ModelManager
from app.agents.commander import CommanderAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent

logger = logging.getLogger("ULTRON.AgentRouter")


class AgentRouter:
    """Modular router matching tasks to their assigned agent handler."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.agents: Dict[str, Any] = {
            "commander": CommanderAgent(model_manager),
            "planner": PlannerAgent(model_manager),
            "researcher": ResearcherAgent(model_manager),
            "coder": CoderAgent(model_manager),
            "reviewer": ReviewerAgent(model_manager),
        }

    def get_agent(self, agent_name: str) -> Any:
        clean_name = agent_name.lower().strip()
        agent = self.agents.get(clean_name)
        if not agent:
            logger.warning("Agent '%s' not found, defaulting to Commander", agent_name)
            return self.agents["commander"]
        return agent

    def select_agent_for_goal(self, goal: str) -> str:
        """Categorize goal and determine primary agent."""
        goal_lower = goal.lower()
        if "code" in goal_lower or "python" in goal_lower or "script" in goal_lower or "function" in goal_lower:
            return "coder"
        elif "research" in goal_lower or "search" in goal_lower or "find" in goal_lower or "compare" in goal_lower:
            return "researcher"
        elif "plan" in goal_lower or "step" in goal_lower:
            return "planner"
        elif "review" in goal_lower or "verify" in goal_lower or "check" in goal_lower:
            return "reviewer"
        return "commander"
