from typing import Dict, Any
from app.ai.model_manager import ModelManager
from app.ai.prompts import CODER_PROMPT


class CoderAgent:
    """Coding Agent: Code generation and syntax evaluation."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    async def generate_code(self, task: str) -> Dict[str, Any]:
        prompt = f"Coding Task: {task}"
        res = await self.model_manager.generate(prompt, system_instruction=CODER_PROMPT)
        return {"agent": "coder", "code": res}
