import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository
from app.intelligence.strategy_engine import StrategyEngine
from app.intelligence.agent_metrics import AgentMetricsEngine
from app.intelligence.memory_consolidator import MemoryConsolidator

logger = logging.getLogger("ULTRON.LearningEngine")


class LearningEngine:
    """Bounded Learning Engine processing execution observations, updating strategy stats,
    recording episodic memories, tracking agent metrics, and detecting patterns without
    self-modifying system parameters or code.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = IntelligenceRepository(db)
        self.strategy_engine = StrategyEngine(db)
        self.metrics_engine = AgentMetricsEngine(db)
        self.consolidator = MemoryConsolidator(db)

    async def process_execution_result(
        self,
        user_id: str,
        execution_id: str,
        goal: str,
        plan: List[Dict[str, Any]],
        tasks_results: List[Dict[str, Any]],
        overall_success: bool,
        duration_ms: int,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Core pipeline: OBSERVE -> ANALYZE -> IDENTIFY_PATTERN -> EVALUATE -> STORE -> UPDATE_STRATEGY."""
        
        # 1. OBSERVE & ANALYZE
        agents_used = list({t.get("agent", "commander") for t in tasks_results})
        tools_used = []
        failures = []
        retries_total = 0
        execution_steps = []
        lessons = []

        for task in tasks_results:
            t_tools = task.get("tools_used", [])
            tools_used.extend(t_tools)
            t_retries = task.get("retry_count", 0)
            retries_total += t_retries

            step_summary = {
                "task_id": task.get("task_id"),
                "agent": task.get("agent"),
                "status": task.get("status"),
                "retries": t_retries
            }
            execution_steps.append(step_summary)

            if task.get("status") == "FAILED" or t_retries > 0:
                failures.append({
                    "task_id": task.get("task_id"),
                    "agent": task.get("agent"),
                    "error": task.get("error") or "Review rejected or task failure"
                })

        tools_used = list(set(tools_used))

        # 2. IDENTIFY_PATTERN & LESSONS
        pattern_detected = "Standard Direct Execution"
        if not overall_success:
            pattern_detected = "Execution Failure Pattern"
            lessons.append(f"Goal '{goal}' failed after {retries_total} retries across agents {agents_used}.")
        else:
            if retries_total > 0:
                pattern_detected = "Retry Recovery Pattern"
                lessons.append(f"Execution succeeded after resolving {retries_total} task retries.")
            else:
                pattern_detected = "Optimal Direct Execution Pattern"
                lessons.append(f"Optimal execution achieved with agents {agents_used} using tools {tools_used}.")

        # 3. EVALUATE & STORE EPISODIC MEMORY
        ep_mem = await self.repo.record_episodic_memory(
            user_id=user_id,
            conversation_id=conversation_id,
            execution_id=execution_id,
            goal=goal,
            plan=plan,
            agents_used=agents_used,
            tools_used=tools_used,
            execution_steps=execution_steps,
            failures=failures,
            retries_count=retries_total,
            duration_ms=duration_ms,
            final_result={"success": overall_success, "total_tasks": len(tasks_results)},
            review_result={"review_passed": overall_success},
            success=overall_success,
            lessons=lessons
        )

        # 4. UPDATE_STRATEGY
        goal_type = self._infer_goal_type(goal)
        await self.strategy_engine.record_strategy_execution(
            goal_type=goal_type,
            description=f"Automated strategy for {goal_type}",
            steps=plan,
            agents=agents_used,
            tools=tools_used,
            success=overall_success,
            duration_ms=duration_ms
        )

        # 5. UPDATE AGENT METRICS
        for task in tasks_results:
            agent = task.get("agent", "commander")
            t_succ = task.get("status") == "COMPLETED"
            t_dur = task.get("duration_ms", 1000)
            t_ret = task.get("retry_count", 0)
            t_tused = task.get("tools_used", [])
            r_score = 1.0 if t_succ else 0.0

            await self.metrics_engine.record_agent_run(
                agent_name=agent,
                success=t_succ,
                duration_ms=t_dur,
                retries=t_ret,
                tools_used=t_tused,
                review_score=r_score
            )

        # 6. LOG LEARNING EVENT
        event = await self.repo.record_learning_event(
            user_id=user_id,
            execution_id=execution_id,
            event_type="EXECUTION_LEARNING",
            observation={"goal": goal, "duration_ms": duration_ms, "success": overall_success},
            pattern_detected=pattern_detected,
            action_taken={
                "recorded_episodic_id": ep_mem.id,
                "updated_strategy_goal_type": goal_type,
                "updated_agents_count": len(agents_used)
            }
        )

        logger.info("Learning engine completed processing execution '%s' (Pattern: %s)",
                    execution_id, pattern_detected)

        return {
            "episodic_id": ep_mem.id,
            "learning_event_id": event.id,
            "pattern_detected": pattern_detected,
            "lessons": lessons,
            "goal_type": goal_type
        }

    @staticmethod
    def _infer_goal_type(goal: str) -> str:
        g = goal.lower()
        if "search" in g or "research" in g or "find" in g:
            return "research_and_compare"
        elif "code" in g or "script" in g or "python" in g or "build" in g:
            return "code_development"
        elif "calculate" in g or "math" in g:
            return "mathematical_computation"
        elif "browser" in g or "scrape" in g or "web" in g:
            return "web_automation"
        elif "computer" in g or "click" in g or "screen" in g:
            return "computer_interaction"
        return "general_problem_solving"
