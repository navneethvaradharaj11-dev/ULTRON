import logging
from typing import Dict, Any, Optional
from app.ai.model_manager import ModelManager
from app.agents.commander import CommanderAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.code_agent import CodeAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.browser_agent import BrowserAgent
from app.agents.computer_agent import ComputerAgent

logger = logging.getLogger("ULTRON.AgentRouter")


class AgentRouter:
    """Modular router matching tasks to their assigned agent handler."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        coder_agent = CoderAgent(model_manager)
        code_agent = CodeAgent(model_manager)
        computer_agent = ComputerAgent()
        self.agents: Dict[str, Any] = {
            "commander": CommanderAgent(model_manager),
            "planner": PlannerAgent(model_manager),
            "researcher": ResearcherAgent(model_manager),
            "coder": coder_agent,
            "code": code_agent,
            "code_agent": code_agent,
            "reviewer": ReviewerAgent(model_manager),
            "browser": BrowserAgent(model_manager),
            "computer": computer_agent,
            "visual": computer_agent,
            "desktop": computer_agent,
            "ui": computer_agent,
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
        if "screen" in goal_lower or "desktop" in goal_lower or "mouse" in goal_lower or "keyboard" in goal_lower or "visual" in goal_lower or "ui" in goal_lower:
            return "computer"
        elif "browser" in goal_lower or "navigate" in goal_lower or "website" in goal_lower or "url" in goal_lower or "click" in goal_lower:
            return "browser"
        elif "code" in goal_lower or "python" in goal_lower or "script" in goal_lower or "function" in goal_lower:
            return "coder"
        elif "research" in goal_lower or "search" in goal_lower or "find" in goal_lower or "compare" in goal_lower:
            return "researcher"
        elif "plan" in goal_lower or "step" in goal_lower:
            return "planner"
        elif "review" in goal_lower or "verify" in goal_lower or "check" in goal_lower:
            return "reviewer"
        return "commander"


