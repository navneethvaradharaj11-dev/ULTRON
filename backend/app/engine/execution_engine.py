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
    """True Agentic AI Execution Engine managing DAG task graphs, observation loops, retries, and observability."""

    def __init__(self, db: AsyncSession, model_manager: Optional[ModelManager] = None):
        self.db = db
        self.model_manager = model_manager or ModelManager()
        self.router = AgentRouter(self.model_manager)
        self.repo = ExecutionRepository(db)
        self.tool_registry = default_tool_registry

    async def run_execution(
        self,
        execution_id: str,
        task_graph: TaskGraph,
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute TaskGraph step-by-step with real-time event streaming and database persistence."""
        start_time = time.time()
        agent_steps_count = 0
        tool_calls_count = 0

        # Update database execution status to RUNNING
        await self.repo.update_execution_status(execution_id, "RUNNING")

        # Emit: execution_started
        start_event = self._build_event(execution_id, "execution_started", {"goal": task_graph.goal, "total_tasks": len(task_graph.tasks)})
        await self.repo.add_event(execution_id, "execution_started", start_event)
        yield start_event

        # Emit: plan_created
        plan_event = self._build_event(execution_id, "plan_created", {"tasks": [t.to_dict() for t in task_graph.tasks.values()]})
        await self.repo.add_event(execution_id, "plan_created", plan_event)
        yield plan_event

        # Persist tasks into database execution_tasks table
        for task_node in task_graph.tasks.values():
            await self.repo.create_execution_task(
                execution_id=execution_id,
                goal=task_node.goal,
                assigned_agent=task_node.assigned_agent,
                description=task_node.description,
                dependencies=task_node.dependencies,
                priority=task_node.priority,
                max_retries=task_node.max_retries
            )
            t_created_event = self._build_event(execution_id, "task_created", {"task_id": task_node.id, "goal": task_node.goal})
            yield t_created_event

        # MAIN AGENT EXECUTION LOOP (Observation Loop)
        while not task_graph.is_complete() and not task_graph.is_failed():
            if agent_steps_count >= settings.MAX_AGENT_STEPS:
                logger.warning("Execution '%s' reached MAX_AGENT_STEPS limit (%d)", execution_id, settings.MAX_AGENT_STEPS)
                task_graph.cancel_all()
                await self.repo.update_execution_status(execution_id, "FAILED")
                fail_event = self._build_event(execution_id, "execution_failed", {"reason": f"Exceeded MAX_AGENT_STEPS limit ({settings.MAX_AGENT_STEPS})"})
                await self.repo.add_event(execution_id, "execution_failed", fail_event)
                yield fail_event
                return

            executable_tasks = task_graph.get_executable_tasks()
            if not executable_tasks:
                if not task_graph.is_complete():
                    logger.error("Execution '%s' blocked: no executable tasks remaining (deadlock/deps)", execution_id)
                    task_graph.cancel_all()
                    await self.repo.update_execution_status(execution_id, "FAILED")
                    fail_event = self._build_event(execution_id, "execution_failed", {"reason": "Task dependency resolution deadlock"})
                    await self.repo.add_event(execution_id, "execution_failed", fail_event)
                    yield fail_event
                    return
                break

            for task_node in executable_tasks:
                agent_steps_count += 1
                task_node.status = TaskStatus.RUNNING
                await self.repo.update_task_status(task_node.id, "RUNNING")

                # Emit: task_started
                t_start_evt = self._build_event(execution_id, "task_started", {"task_id": task_node.id, "agent": task_node.assigned_agent, "goal": task_node.goal})
                await self.repo.add_event(execution_id, "task_started", t_start_evt)
                yield t_start_evt

                # Dispatch Task to Agent
                agent = self.router.get_agent(task_node.assigned_agent)
                agent_start_evt = self._build_event(execution_id, "agent_started", {"agent": task_node.assigned_agent, "task_id": task_node.id})
                yield agent_start_evt

                # Execute Observation Loop for Task Node
                task_success = False
                while task_node.retry_count <= task_node.max_retries:
                    try:
                        # 1. ACT: Execute Agent & Tool
                        exec_res = await self._execute_task_node(execution_id, task_node, agent, user_id)
                        
                        # Emit tool events if tool was invoked
                        for tool_name in exec_res.tools_used:
                            tool_calls_count += 1
                            t_evt = self._build_event(execution_id, "tool_started", {"tool_name": tool_name, "task_id": task_node.id})
                            yield t_evt
                            t_done_evt = self._build_event(execution_id, "tool_completed", {"tool_name": tool_name, "task_id": task_node.id})
                            yield t_done_evt

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

                        # 2. EVALUATE: Review Output if agent is not reviewer
                        if task_node.assigned_agent != "reviewer":
                            rev_start_evt = self._build_event(execution_id, "review_started", {"task_id": task_node.id})
                            yield rev_start_evt

                            reviewer = self.router.get_agent("reviewer")
                            output_str = str(exec_res.output.get("response", exec_res.output))
                            review_res: ReviewResult = await reviewer.review(output_str)

                            rev_done_evt = self._build_event(execution_id, "review_completed", {
                                "task_id": task_node.id,
                                "status": review_res.status,
                                "confidence": review_res.confidence,
                                "issues": review_res.issues
                            })
                            yield rev_done_evt

                            if review_res.status == "rejected" and task_node.retry_count < task_node.max_retries:
                                task_node.retry_count += 1
                                logger.warning("Task '%s' review rejected. Retrying (%d/%d)...", task_node.id, task_node.retry_count, task_node.max_retries)
                                continue

                        # Mark task completed
                        task_node.status = TaskStatus.COMPLETED
                        task_node.output_data = exec_res.output
                        task_node.completed_at = datetime.utcnow()
                        await self.repo.update_task_status(task_node.id, "COMPLETED", output_json=exec_res.output)
                        
                        agent_done_evt = self._build_event(execution_id, "agent_completed", {"agent": task_node.assigned_agent, "task_id": task_node.id})
                        yield agent_done_evt

                        t_comp_evt = self._build_event(execution_id, "task_completed", {"task_id": task_node.id, "output": exec_res.output})
                        await self.repo.add_event(execution_id, "task_completed", t_comp_evt)
                        yield t_comp_evt
                        
                        task_success = True
                        break

                    except Exception as e:
                        logger.error("Task '%s' exception: %s", task_node.id, e)
                        task_node.retry_count += 1
                        if task_node.retry_count > task_node.max_retries:
                            task_node.status = TaskStatus.FAILED
                            await self.repo.update_task_status(task_node.id, "FAILED", output_json={"error": str(e)})
                            t_fail_evt = self._build_event(execution_id, "task_failed", {"task_id": task_node.id, "error": str(e)})
                            await self.repo.add_event(execution_id, "task_failed", t_fail_evt)
                            yield t_fail_evt
                            break

                if not task_success and task_node.status == TaskStatus.FAILED:
                    task_graph.cancel_all()
                    await self.repo.update_execution_status(execution_id, "FAILED")
                    exec_fail_evt = self._build_event(execution_id, "execution_failed", {"task_id": task_node.id, "reason": "Sub-task failed after retries"})
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

    async def _execute_task_node(
        self,
        execution_id: str,
        task_node: TaskNode,
        agent: Any,
        user_id: str
    ) -> AgentExecutionResult:
        """Run agent logic for a specific TaskNode."""
        start_t = time.time()
        
        # Check tool execution triggers for goal
        goal_lower = task_node.goal.lower()
        if "calculate" in goal_lower or "math" in goal_lower:
            expr = task_node.goal.replace("calculate", "").replace("math", "").strip(" ?:=")
            tool_res = await self.tool_registry.execute_tool("calculator", {"expression": expr}, user_id=user_id, db=self.db)
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
            res = {"response": f"Executed agent '{task_node.assigned_agent}' for task '{task_node.goal}'"}

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

    def _build_event(self, execution_id: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:8]}",
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "payload": payload
        }
