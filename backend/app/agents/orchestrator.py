import logging
from typing import Dict, Any, List
from app.ai.model_manager import ModelManager
from app.agents.commander import CommanderAgent
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent

logger = logging.getLogger("ULTRON.Orchestrator")


class AgentOrchestrator:
    """Coordinates agent execution routines for ULTRON Core."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.commander = CommanderAgent(model_manager)
        self.planner = PlannerAgent(model_manager)
        self.researcher = ResearcherAgent(model_manager)
        self.coder = CoderAgent(model_manager)
        self.reviewer = ReviewerAgent(model_manager)

    async def run_workflow(self, user_input: str, context: str) -> Dict[str, Any]:
        logger.info("Orchestrator initiating workflow for request: '%s'", user_input)

        # 1. Commander Agent evaluates intent
        cmd_result = await self.commander.execute(user_input, context)

        # 2. Check if planning or tool calls are implied
        input_lower = user_input.lower()
        plan_data = None
        if "plan" in input_lower or "steps" in input_lower:
            plan_data = await self.planner.plan(user_input)

        return {
            "commander_response": cmd_result["response"],
            "plan": plan_data,
            "status": "completed"
        }
