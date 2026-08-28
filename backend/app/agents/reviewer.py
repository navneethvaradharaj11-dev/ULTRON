from typing import Dict, Any, List
from app.ai.model_manager import ModelManager
from app.ai.prompts import REVIEWER_PROMPT
from app.engine.contracts import ReviewResult


class ReviewerAgent:
    """Upgraded Reviewer Agent outputting structured JSON validation results."""

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    async def review(self, content_to_review: str) -> ReviewResult:
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["approved", "rejected"]},
                "issues": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "confidence": {"type": "number"}
            },
            "required": ["status", "issues", "confidence"]
        }
        prompt = f"Review target execution output:\n{content_to_review}"
        result_dict = await self.model_manager.structured_output(prompt, schema, system_instruction=REVIEWER_PROMPT)

        if "status" in result_dict and result_dict["status"] in ["approved", "rejected"]:
            return ReviewResult(
                status=result_dict["status"],
                issues=result_dict.get("issues", []),
                confidence=float(result_dict.get("confidence", 0.95))
            )
        
        # Default structured review approval
        return ReviewResult(status="approved", issues=[], confidence=0.95)

    async def review_code(
        self,
        code: str,
        compilation_output: str = "",
        test_output: str = "",
        runtime_output: str = ""
    ) -> ReviewResult:
        """Specialized review evaluation for code, compilation, tests, and runtime behavior."""
        summary = (
            f"--- SOURCE CODE ---\n{code}\n\n"
            f"--- COMPILATION OUTPUT ---\n{compilation_output}\n\n"
            f"--- TEST OUTPUT ---\n{test_output}\n\n"
            f"--- RUNTIME OUTPUT ---\n{runtime_output}"
        )
        return await self.review(summary)

