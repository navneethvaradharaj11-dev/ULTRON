from typing import Dict, Any, Optional
from app.ai.model_manager import ModelManager
from app.ai.prompts import COMMANDER_PROMPT


class CommanderAgent:
    """Commander Agent: Decides execution strategy and delegates to specialized agents."""

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()


    async def execute(self, user_input: str, context: str) -> Dict[str, Any]:
        prompt = f"User Request: {user_input}\nContext:\n{context}\nDetermine strategy and output direct response or tool directive."
        response = await self.model_manager.generate(prompt, system_instruction=COMMANDER_PROMPT)
        return {"agent": "commander", "response": response}

    async def analyze_intent(self, goal: str) -> Dict[str, Any]:
        """Analyze intent and classify goal type."""
        lower_goal = goal.lower()
        if "research" in lower_goal or "search" in lower_goal or "find" in lower_goal:
            intent_type = "research_and_synthesis"
        elif "code" in lower_goal or "python" in lower_goal or "build" in lower_goal or "script" in lower_goal or "calculate" in lower_goal:
            intent_type = "mathematical_computation" if "calculate" in lower_goal or "*" in lower_goal or "+" in lower_goal else "software_development"
        elif "browser" in lower_goal or "website" in lower_goal:
            intent_type = "web_navigation"
        else:
            intent_type = "general_execution"
        return {"intent": intent_type, "goal": goal}

