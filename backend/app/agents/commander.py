from typing import Dict, Any
from app.ai.model_manager import ModelManager
from app.ai.prompts import COMMANDER_PROMPT


class CommanderAgent:
    """Commander Agent: Decides execution strategy and delegates to specialized agents."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    async def execute(self, user_input: str, context: str) -> Dict[str, Any]:
        prompt = f"User Request: {user_input}\nContext:\n{context}\nDetermine strategy and output direct response or tool directive."
        response = await self.model_manager.generate(prompt, system_instruction=COMMANDER_PROMPT)
        return {"agent": "commander", "response": response}
