import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("ULTRON.IntentEngine")


class StructuredIntent(BaseModel):
    intent_type: str = Field(default="GENERAL_GOAL")
    goal: str
    constraints: Dict[str, Any] = Field(default_factory=dict)
    required_capabilities: list = Field(default_factory=list)
    risk_level: str = Field(default="LOW")
    urgency: str = Field(default="MEDIUM")
    required_approval: bool = Field(default=False)


class IntentEngine:
    """Parses natural language user messages into structured intent goals."""

    @staticmethod
    def parse_intent(message: str) -> StructuredIntent:
        msg_lower = message.lower().strip()

        intent_type = "GENERAL_GOAL"
        risk_level = "LOW"
        required_approval = False
        caps = []

        if "research" in msg_lower or "search" in msg_lower or "google" in msg_lower:
            intent_type = "RESEARCH_AND_ANALYSIS"
            caps.append("research")
            caps.append("browser")

        if "code" in msg_lower or "python" in msg_lower or "c++" in msg_lower or "c implementation" in msg_lower or "implementation" in msg_lower or "fix" in msg_lower:
            if intent_type == "GENERAL_GOAL":
                intent_type = "CODE_GENERATION_AND_TEST"
            caps.append("code")
            caps.append("sandbox")


        if "pdf" in msg_lower or "document" in msg_lower or "csv" in msg_lower or "file" in msg_lower:
            intent_type = "KNOWLEDGE_QUERY"
            caps.append("knowledge")

        if "submit" in msg_lower or "delete" in msg_lower or "purchase" in msg_lower:
            risk_level = "HIGH"
            required_approval = True

        if not caps:
            caps = ["workflows", "memory"]

        return StructuredIntent(
            intent_type=intent_type,
            goal=message,
            required_capabilities=caps,
            risk_level=risk_level,
            required_approval=required_approval
        )
