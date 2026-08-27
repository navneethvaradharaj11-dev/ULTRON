from typing import Dict, Any
from app.ai.model_manager import ModelManager
from app.ai.prompts import RESEARCHER_PROMPT


class ResearcherAgent:
    """Researcher Agent: Info gathering and research synthesis."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    async def research(self, topic: str) -> Dict[str, Any]:
        prompt = f"Research Topic: {topic}"
        res = await self.model_manager.generate(prompt, system_instruction=RESEARCHER_PROMPT)
        return {"agent": "researcher", "findings": res}
