import time
import uuid
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.ai.model_manager import ModelManager
from app.engine.contracts import TaskStatus, AgentExecutionResult, ReviewResult
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.router import AgentRouter
from app.tools.registry import default_tool_registry
from app.database.repositories.execution_repo import ExecutionRepository

logger = logging.getLogger("ULTRON.ExecutionEngine")


class AgentExecutionEngine:
    """True Agentic AI Execution Engine managing DAG task graphs,
    observation loops, retries, metrics, and observability.

    Phase 2.5 additions:
    - Per-task metric recording (duration, review confidence, retry count)
    - resume_execution: rebuild TaskGraph from DB, skip already-completed tasks
    """

    def __init__(self, db: AsyncSession, model_manager: Optional[ModelManager] = None):
        self.db = db
        self.model_manager = model_manager or ModelManager()
        self.router = AgentRouter(self.model_manager)
        self.repo = ExecutionRepository(db)
        self.tool_registry = default_tool_registry

    # ------------------------------------------------------------------
    # Phase 2.5: Resume execution from persisted state
    # ------------------------------------------------------------------

    async def rebuild_graph_from_db(
        self, execution_id: str
    ) -> Optional[TaskGraph]:
        """Rebuild a TaskGraph from the DB, marking tasks that are already COMPLETED.

        RUNNING tasks are reset to PENDING so they will be re-executed.
        Returns None if the execution does not exist or is already terminal.
        """
        execution = await self.repo.get_execution_by_id(execution_id)
        if not execution:
            return None
        if execution.status in ("COMPLETED", "FAILED", "CANCELLED"):
            logger.info("Execution '%s' is terminal (%s) — cannot resume.", execution_id, execution.status)
            return None

        # Reset orphaned RUNNING tasks (process died mid-task)
        reset = await self.repo.reset_running_tasks_to_pending(execution_id)
        if reset:
            logger.info("Resumed execution '%s': reset %d RUNNING task(s) to PENDING.", execution_id, reset)

        db_tasks = await self.repo.get_execution_tasks(execution_id)
        graph = TaskGraph(execution_id, execution.goal)

        for db_task in db_tasks:
            node = TaskNode(
                task_id=db_task.id,
                goal=db_task.goal,
                assigned_agent=db_task.assigned_agent,
                description=db_task.description or "",
                dependencies=db_task.dependencies_json or [],
                priority=db_task.priority,
                max_retries=db_task.max_retries,
            )
            # Restore completed state so DAG resolves correctly
            if db_task.status == "COMPLETED":
                node.status = TaskStatus.COMPLETED
                node.output_data = db_task.output_json or {}
            elif db_task.status in ("FAILED", "CANCELLED"):
                node.status = TaskStatus(db_task.status)
            # PENDING / WAITING → leave as PENDING
            graph.add_task(node)

        return graph

    # ------------------------------------------------------------------
    # Main execution loop
    # ------------------------------------------------------------------

    async def run_execution(
        self,
        execution_id: str,
        task_graph: TaskGraph,
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute TaskGraph step-by-step with real-time event streaming and DB persistence."""
        start_time = time.time()
        agent_steps_count = 0
        tool_calls_count = 0

        await self.repo.update_execution_status(execution_id, "RUNNING")

        start_event = self._build_event(execution_id, "execution_started", {
            "goal": task_graph.goal,
            "total_tasks": len(task_graph.tasks)
        })
        await self.repo.add_event(execution_id, "execution_started", start_event)
        yield start_event

        plan_event = self._build_event(execution_id, "plan_created", {
            "tasks": [t.to_dict() for t in task_graph.tasks.values()]
        })
        await self.repo.add_event(execution_id, "plan_created", plan_event)
        yield plan_event

        # Persist only tasks that are not already in DB (resume scenario: skip existing)
        existing_db_tasks = await self.repo.get_execution_tasks(execution_id)
        existing_task_ids = {t.id for t in existing_db_tasks}

        for task_node in task_graph.tasks.values():
            if task_node.id not in existing_task_ids:
                await self.repo.create_execution_task(
                    execution_id=execution_id,
                    goal=task_node.goal,
                    assigned_agent=task_node.assigned_agent,
                    description=task_node.description,
                    dependencies=task_node.dependencies,
                    priority=task_node.priority,
                    max_retries=task_node.max_retries
                )
            t_created_event = self._build_event(execution_id, "task_created", {
                "task_id": task_node.id,
                "goal": task_node.goal
            })
            yield t_created_event

        # ---------------------------------------------------------------
        # MAIN AGENT EXECUTION LOOP (Observation Loop)
        # ---------------------------------------------------------------
        while not task_graph.is_complete() and not task_graph.is_failed():
            if agent_steps_count >= settings.MAX_AGENT_STEPS:
                logger.warning("Execution '%s' reached MAX_AGENT_STEPS limit (%d)",
                               execution_id, settings.MAX_AGENT_STEPS)
                task_graph.cancel_all()
                await self.repo.update_execution_status(execution_id, "FAILED")
                fail_event = self._build_event(execution_id, "execution_failed", {
                    "reason": f"Exceeded MAX_AGENT_STEPS limit ({settings.MAX_AGENT_STEPS})"
                })
                await self.repo.add_event(execution_id, "execution_failed", fail_event)
                yield fail_event
                return

            executable_tasks = task_graph.get_executable_tasks()
            if not executable_tasks:
                if not task_graph.is_complete():
                    logger.error("Execution '%s' deadlock: no executable tasks.", execution_id)
                    task_graph.cancel_all()
                    await self.repo.update_execution_status(execution_id, "FAILED")
                    fail_event = self._build_event(execution_id, "execution_failed", {
                        "reason": "Task dependency resolution deadlock"
                    })
                    await self.repo.add_event(execution_id, "execution_failed", fail_event)
                    yield fail_event
                    return
                break

            for task_node in executable_tasks:
                agent_steps_count += 1
                task_node.status = TaskStatus.RUNNING
                await self.repo.update_task_status(task_node.id, "RUNNING")

                t_start_evt = self._build_event(execution_id, "task_started", {
                    "task_id": task_node.id,
                    "agent": task_node.assigned_agent,
                    "goal": task_node.goal
                })
                await self.repo.add_event(execution_id, "task_started", t_start_evt)
                yield t_start_evt

                agent = self.router.get_agent(task_node.assigned_agent)
                agent_start_evt = self._build_event(execution_id, "agent_started", {
                    "agent": task_node.assigned_agent,
                    "task_id": task_node.id
                })
                yield agent_start_evt

                task_success = False
                review_status_final: Optional[str] = None
                review_confidence_final: float = 0.0

                while task_node.retry_count <= task_node.max_retries:
                    try:
                        exec_res = await self._execute_task_node(execution_id, task_node, agent, user_id)

                        for tool_name in exec_res.tools_used:
                            tool_calls_count += 1
                            yield self._build_event(execution_id, "tool_started", {
                                "tool_name": tool_name, "task_id": task_node.id
                            })
                            yield self._build_event(execution_id, "tool_completed", {
                                "tool_name": tool_name, "task_id": task_node.id
                            })

                        if exec_res.status == TaskStatus.REQUIRES_APPROVAL:
                            task_node.status = TaskStatus.REQUIRES_APPROVAL
                            await self.repo.update_task_status(task_node.id, "REQUIRES_APPROVAL")
                            appr_evt = self._build_event(execution_id, "approval_required", {
                                "task_id": task_node.id,
                                "tool_name": exec_res.tools_used[0] if exec_res.tools_used else "filesystem_write",
                                "message": exec_res.output.get("message", "Tool requires explicit user approval.")
                            })
                            await self.repo.add_event(execution_id, "approval_required", appr_evt)
                            yield appr_evt
                            return

                        # EVALUATE: Reviewer gate (skip for reviewer itself)
                        if task_node.assigned_agent != "reviewer":
                            yield self._build_event(execution_id, "review_started", {"task_id": task_node.id})
                            reviewer = self.router.get_agent("reviewer")
                            output_str = str(exec_res.output.get("response", exec_res.output))
                            review_res: ReviewResult = await reviewer.review(output_str)
                            review_status_final = review_res.status
                            review_confidence_final = review_res.confidence

                            yield self._build_event(execution_id, "review_completed", {
                                "task_id": task_node.id,
                                "status": review_res.status,
                                "confidence": review_res.confidence,
                                "issues": review_res.issues
                            })

                            if review_res.status == "rejected" and task_node.retry_count < task_node.max_retries:
                                task_node.retry_count += 1
                                logger.warning("Task '%s' review rejected. Retry %d/%d.",
                                               task_node.id, task_node.retry_count, task_node.max_retries)
                                continue
                        else:
                            review_status_final = "skipped"
                            review_confidence_final = 1.0

                        # Mark task COMPLETED
                        task_node.status = TaskStatus.COMPLETED
                        task_node.output_data = exec_res.output
                        task_node.completed_at = datetime.utcnow()
                        await self.repo.update_task_status(task_node.id, "COMPLETED", output_json=exec_res.output)

                        # Record metrics for this task
                        await self.repo.record_metrics(
                            execution_id=execution_id,
                            task_id=task_node.id,
                            agent_name=exec_res.agent_name,
                            duration_ms=exec_res.duration_ms,
                            status="COMPLETED",
                            retry_count=task_node.retry_count,
                            tools_used=exec_res.tools_used,
                            review_status=review_status_final,
                            review_confidence=review_confidence_final
                        )

                        yield self._build_event(execution_id, "agent_completed", {
                            "agent": task_node.assigned_agent,
                            "task_id": task_node.id
                        })
                        t_comp_evt = self._build_event(execution_id, "task_completed", {
                            "task_id": task_node.id,
                            "output": exec_res.output
                        })
                        await self.repo.add_event(execution_id, "task_completed", t_comp_evt)
                        yield t_comp_evt
                        task_success = True
                        break

                    except Exception as e:
                        logger.error("Task '%s' exception: %s", task_node.id, e)
                        task_node.retry_count += 1
                        if task_node.retry_count > task_node.max_retries:
                            task_node.status = TaskStatus.FAILED
                            await self.repo.update_task_status(task_node.id, "FAILED",
                                                               output_json={"error": str(e)})
                            # Record failure metrics
                            await self.repo.record_metrics(
                                execution_id=execution_id,
                                task_id=task_node.id,
                                agent_name=task_node.assigned_agent,
                                duration_ms=0,
                                status="FAILED",
                                retry_count=task_node.retry_count,
                            )
                            t_fail_evt = self._build_event(execution_id, "task_failed", {
                                "task_id": task_node.id,
                                "error": str(e)
                            })
                            await self.repo.add_event(execution_id, "task_failed", t_fail_evt)
                            yield t_fail_evt
                            break

                if not task_success and task_node.status == TaskStatus.FAILED:
                    task_graph.cancel_all()
                    await self.repo.update_execution_status(execution_id, "FAILED")
                    exec_fail_evt = self._build_event(execution_id, "execution_failed", {
                        "task_id": task_node.id,
                        "reason": "Sub-task failed after retries"
                    })
                    await self.repo.add_event(execution_id, "execution_failed", exec_fail_evt)
                    yield exec_fail_evt
                    return

        # Complete Execution
        await self.repo.update_execution_status(execution_id, "COMPLETED")
        duration_ms = int((time.time() - start_time) * 1000)
        final_evt = self._build_event(execution_id, "execution_completed", {
            "status": "COMPLETED",
            "duration_ms": duration_ms,
            "tasks_summary": [t.to_dict() for t in task_graph.tasks.values()]
        })
        await self.repo.add_event(execution_id, "execution_completed", final_evt)
        yield final_evt

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _execute_task_node(
        self,
        execution_id: str,
        task_node: TaskNode,
        agent: Any,
        user_id: str
    ) -> AgentExecutionResult:
        """Run agent logic for a specific TaskNode."""
        start_t = time.time()

        goal_lower = task_node.goal.lower()
        if "calculate" in goal_lower or "math" in goal_lower:
            expr = task_node.goal.replace("calculate", "").replace("math", "").strip(" ?:=")
            tool_res = await self.tool_registry.execute_tool(
                "calculator", {"expression": expr}, user_id=user_id, db=self.db
            )
            duration_ms = int((time.time() - start_t) * 1000)
            return AgentExecutionResult(
                execution_id=execution_id,
                agent_name="calculator_tool",
                task_id=task_node.id,
                status=TaskStatus.COMPLETED if tool_res.get("success") else TaskStatus.FAILED,
                output={"response": f"Calculation Result: {tool_res.get('result')}"},
                tools_used=["calculator"],
                duration_ms=duration_ms
            )

        if hasattr(agent, "execute"):
            res = await agent.execute(task_node.goal, context=task_node.description)
        elif hasattr(agent, "research"):
            res = await agent.research(task_node.goal)
        elif hasattr(agent, "generate_code"):
            res = await agent.generate_code(task_node.goal)
        else:
            res = {"response": f"Executed agent '{task_node.assigned_agent}' for goal '{task_node.goal}'"}

        duration_ms = int((time.time() - start_t) * 1000)
        return AgentExecutionResult(
            execution_id=execution_id,
            agent_name=task_node.assigned_agent,
            task_id=task_node.id,
            status=TaskStatus.COMPLETED,
            output=res if isinstance(res, dict) else {"response": str(res)},
            tools_used=[],
            duration_ms=duration_ms
        )

    def _build_event(
        self, execution_id: str, event_type: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "payload": payload
        }
