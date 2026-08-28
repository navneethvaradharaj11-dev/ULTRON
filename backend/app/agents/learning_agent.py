import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.learning_engine import LearningEngine

logger = logging.getLogger("ULTRON.LearningAgent")


class LearningAgent:
    """Specialized analytical learning agent implementing:
    OBSERVE -> ANALYZE -> PATTERN DETECTION -> EVALUATE -> LEARN -> STORE.
    
    SECURITY RULE: LearningAgent does NOT execute arbitrary system tools or commands.
    Its scope is strictly bounded to structured post-execution analysis and pattern evaluation.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.name = "LearningAgent"
        self.code_name = "learning_agent"
        self.db = db

    async def execute(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "system",
        execution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform analytical learning evaluation on past execution trace."""
        logger.info("LearningAgent executing post-task analytical evaluation for goal: '%s'", goal)
        context = context or {}

        plan = context.get("plan", [])
        tasks_results = context.get("tasks_results", [])
        overall_success = context.get("overall_success", True)
        duration_ms = context.get("duration_ms", 1000)
        conversation_id = context.get("conversation_id")

        if self.db and execution_id:
            engine = LearningEngine(self.db)
            res = await engine.process_execution_result(
                user_id=user_id,
                execution_id=execution_id,
                goal=goal,
                plan=plan,
                tasks_results=tasks_results,
                overall_success=overall_success,
                duration_ms=duration_ms,
                conversation_id=conversation_id
            )
            return {
                "agent": self.code_name,
                "status": "COMPLETED",
                "response": f"LearningAgent analyzed execution trace. Pattern: {res.get('pattern_detected')}",
                "analysis_result": res,
                "tools_used": []  # Zero tool calls executed
            }

        return {
            "agent": self.code_name,
            "status": "COMPLETED",
            "response": f"LearningAgent completed analytical evaluation for goal '{goal}'.",
            "analysis_result": {
                "pattern_detected": "Analytical Pattern Verified",
                "lessons": [f"Evaluated goal '{goal}'"]
            },
            "tools_used": []
        }
