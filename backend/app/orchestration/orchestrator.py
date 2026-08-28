import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestration.workflow import Workflow, WorkflowStep, WorkflowResult
from app.orchestration.workflow_state import WorkflowState, is_valid_transition
from app.orchestration.workflow_planner import WorkflowPlanner
from app.orchestration.task_scheduler import TaskScheduler
from app.orchestration.agent_coordinator import AgentCoordinator
from app.orchestration.failure_manager import FailureManager
from app.orchestration.recovery_engine import RecoveryEngine
from app.orchestration.replanning_engine import ReplanningEngine
from app.orchestration.checkpoint_manager import CheckpointManager
from app.orchestration.approval_coordinator import ApprovalCoordinator
from app.orchestration.result_aggregator import ResultAggregator
from app.orchestration.orchestration_policy import default_orchestration_policy
from app.security.orchestration_security import OrchestrationSecurity
from app.database.repositories.workflow_repo import WorkflowRepository
from app.intelligence.learning_engine import LearningEngine
from app.intelligence.memory_engine import MemoryEngine

logger = logging.getLogger(__name__)

class WorkflowOrchestrator:
    """Central Autonomous Workflow Orchestrator driving the complete Phase 7 lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = WorkflowRepository(db)
        self.security = OrchestrationSecurity(default_orchestration_policy)
        self.planner = WorkflowPlanner(db)
        self.agent_coordinator = AgentCoordinator(db)
        self.replanner = ReplanningEngine(max_replans=default_orchestration_policy.max_replans)
        self.checkpoint_mgr = CheckpointManager(db)
        self.approval_coord = ApprovalCoordinator(db)
        self.learning_engine = LearningEngine(db)
        self.memory_engine = MemoryEngine(db)

    async def create_workflow(self, user_id: str, goal: str) -> Workflow:
        """Initialize workflow record in database."""
        wf_model = await self.repo.create_workflow(user_id=user_id, goal=goal)
        wf = Workflow(
            workflow_id=wf_model.id,
            user_id=user_id,
            goal=goal,
            current_state=WorkflowState.CREATED
        )
        await self.repo.create_event(wf.workflow_id, "workflow_created", {"goal": goal})
        return wf

    async def execute_workflow(
        self,
        workflow_id: str,
        user_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute full autonomous workflow lifecycle yielding real-time events."""
        wf_model = await self.repo.get_workflow(workflow_id, user_id)
        if not wf_model:
            yield {"event_type": "workflow_failed", "workflow_id": workflow_id, "error": "Workflow not found"}
            return

        self.security.validate_tenant_ownership(wf_model.user_id, user_id)

        # 1. Transition -> UNDERSTANDING
        await self._transition_state(workflow_id, user_id, WorkflowState.UNDERSTANDING)
        yield {"event_type": "workflow_understanding", "workflow_id": workflow_id, "state": "UNDERSTANDING"}

        # 2. Memory Lookup & Strategy Selection -> PLANNING
        await self._transition_state(workflow_id, user_id, WorkflowState.PLANNING)
        yield {"event_type": "workflow_memory_lookup", "workflow_id": workflow_id}

        try:
            plan_res = await self.planner.plan_workflow(
                user_id=user_id,
                goal=wf_model.goal,
                execution_id=wf_model.execution_id or f"exec_{workflow_id}"
            )
        except Exception as e:
            logger.error("Planning failed for workflow '%s': %s", workflow_id, e)
            await self._transition_state(workflow_id, user_id, WorkflowState.FAILED)
            yield {"event_type": "workflow_failed", "workflow_id": workflow_id, "error": str(e)}
            return

        strategy_id = plan_res.get("strategy_id")
        graph = plan_res["graph"]
        plan_nodes = plan_res["plan_nodes"]

        # Persist steps to DB
        for node in plan_nodes:
            await self.repo.create_step(
                workflow_id=workflow_id,
                step_id=node["task_id"],
                name=node["goal"],
                assigned_agent=node.get("assigned_agent", "commander"),
                dependencies=node.get("dependencies", []),
                input_data=node.get("input", {})
            )

        yield {
            "event_type": "workflow_strategy_selected",
            "workflow_id": workflow_id,
            "strategy_id": strategy_id,
            "strategy": plan_res.get("strategy")
        }

        yield {
            "event_type": "workflow_plan_created",
            "workflow_id": workflow_id,
            "tasks_count": len(plan_nodes),
            "plan_nodes": plan_nodes
        }

        # Save checkpoint
        await self.checkpoint_mgr.save_checkpoint(
            workflow_id=workflow_id,
            checkpoint_name="plan_validated",
            state_snapshot={"plan_nodes": plan_nodes, "strategy_id": strategy_id}
        )
        yield {"event_type": "workflow_checkpoint_created", "workflow_id": workflow_id, "checkpoint": "plan_validated"}

        # 3. Transition -> READY & RUNNING
        await self._transition_state(workflow_id, user_id, WorkflowState.READY)
        await self._transition_state(workflow_id, user_id, WorkflowState.RUNNING)
        yield {"event_type": "workflow_started", "workflow_id": workflow_id, "state": "RUNNING"}

        scheduler = TaskScheduler(graph)
        completed_tasks: Set[str] = set()
        failed_tasks: Set[str] = set()
        tasks_results: List[Dict[str, Any]] = []

        # 4. Execution Loop
        start_time = datetime.utcnow()
        while not scheduler.is_workflow_complete():
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            self.security.check_duration(elapsed)

            ready_nodes = scheduler.get_ready_tasks(completed_tasks, failed_tasks)
            if not ready_nodes and not scheduler.is_workflow_complete():
                # Check for deadlock or unresolvable failure
                logger.warning("No ready tasks available in workflow '%s', breaking loop", workflow_id)
                break

            # Parallel Group Execution
            parallel_group = [n.task_id for n in ready_nodes]
            yield {
                "event_type": "workflow_parallel_group_started",
                "workflow_id": workflow_id,
                "tasks": parallel_group
            }

            for node in ready_nodes:
                node.status = "RUNNING"
                await self.repo.update_step(workflow_id, node.task_id, "RUNNING")
                yield {
                    "event_type": "workflow_step_started",
                    "workflow_id": workflow_id,
                    "task_id": node.task_id,
                    "agent": node.assigned_agent,
                    "goal": node.goal
                }

                # Dispatch execution
                try:
                    res = await self.agent_coordinator.execute_task(
                        task_id=node.task_id,
                        goal=node.goal,
                        assigned_agent=node.assigned_agent,
                        user_id=user_id,
                        execution_id=wf_model.execution_id or f"exec_{workflow_id}"
                    )

                    if res.get("status") == "COMPLETED":
                        node.status = "COMPLETED"
                        completed_tasks.add(node.task_id)
                        await self.repo.update_step(workflow_id, node.task_id, "COMPLETED", output_data=res)
                        tasks_results.append(res)
                        yield {
                            "event_type": "workflow_step_completed",
                            "workflow_id": workflow_id,
                            "task_id": node.task_id,
                            "agent": node.assigned_agent,
                            "result": res
                        }
                    else:
                        raise RuntimeError(res.get("error") or "Task execution returned non-complete status")

                except Exception as ex:
                    node.status = "FAILED"
                    failed_tasks.add(node.task_id)
                    failure_info = FailureManager.classify_failure(ex)
                    await self.repo.record_failure(
                        workflow_id=workflow_id,
                        task_id=node.task_id,
                        agent=node.assigned_agent,
                        failure_type=failure_info["failure_type"],
                        error_message=failure_info["error_message"],
                        context=failure_info["context"],
                        recoverable=failure_info["recoverable"]
                    )
                    yield {
                        "event_type": "workflow_step_failed",
                        "workflow_id": workflow_id,
                        "task_id": node.task_id,
                        "failure_type": failure_info["failure_type"],
                        "error": failure_info["error_message"]
                    }

                    # Recovery / Replanning
                    rec_action = RecoveryEngine.determine_recovery_action(
                        failure_type=failure_info["failure_type"],
                        task_id=node.task_id,
                        agent=node.assigned_agent,
                        retry_count=node.retry_count
                    )

                    if rec_action["action"] == "RETRY_TASK":
                        yield {"event_type": "workflow_recovery_started", "workflow_id": workflow_id, "action": "RETRY_TASK"}
                        node.retry_count += 1
                        node.status = "PENDING"
                        failed_tasks.remove(node.task_id)
                        yield {"event_type": "workflow_recovery_completed", "workflow_id": workflow_id, "status": "RETRYING"}
                    elif rec_action["action"] == "REPLAN_OR_FAIL":
                        yield {"event_type": "workflow_replan_started", "workflow_id": workflow_id}
                        graph = self.replanner.replan_graph(graph, node.task_id, failure_info["error_message"], wf_model.replan_count)
                        wf_model.replan_count += 1
                        scheduler = TaskScheduler(graph)
                        yield {"event_type": "workflow_replan_completed", "workflow_id": workflow_id}
                    elif rec_action["action"] == "STOP":
                        await self._transition_state(workflow_id, user_id, WorkflowState.FAILED)
                        yield {"event_type": "workflow_failed", "workflow_id": workflow_id, "error": "Security failure encountered"}
                        return

            yield {
                "event_type": "workflow_parallel_group_completed",
                "workflow_id": workflow_id,
                "tasks": parallel_group
            }

            # Update progress
            progress = scheduler.get_progress()
            await self.repo.update_workflow_state(workflow_id, user_id, WorkflowState.RUNNING, progress=progress)

        # 5. Transition -> VERIFYING
        await self._transition_state(workflow_id, user_id, WorkflowState.VERIFYING)
        yield {"event_type": "workflow_verification_started", "workflow_id": workflow_id}

        # Verification Gate
        unresolved_failures = len(failed_tasks)
        if unresolved_failures > 0 and not completed_tasks:
            await self._transition_state(workflow_id, user_id, WorkflowState.FAILED)
            yield {"event_type": "workflow_verification_completed", "workflow_id": workflow_id, "status": "FAILED"}
            yield {"event_type": "workflow_failed", "workflow_id": workflow_id, "error": "Verification gate failed"}
            return

        yield {"event_type": "workflow_verification_completed", "workflow_id": workflow_id, "status": "PASSED"}

        # 6. Aggregate Results
        res_obj = ResultAggregator.aggregate_results(
            workflow_id=workflow_id,
            goal=wf_model.goal,
            tasks_results=tasks_results
        )

        await self.repo.create_result(
            workflow_id=workflow_id,
            summary=res_obj.summary,
            status=res_obj.status,
            confidence=res_obj.confidence,
            evidence=res_obj.evidence,
            tasks_completed=res_obj.tasks_completed,
            tasks_failed=res_obj.tasks_failed,
            warnings=res_obj.warnings
        )

        # 7. Memory & Learning Integration (Phase 6)
        try:
            await self.learning_engine.process_execution_result(
                user_id=user_id,
                execution_id=wf_model.execution_id or f"exec_{workflow_id}",
                goal=wf_model.goal,
                plan=plan_nodes,
                tasks_results=tasks_results,
                overall_success=(res_obj.status == "COMPLETED"),
                duration_ms=int(elapsed * 1000)
            )
        except Exception as l_err:
            logger.warning("Learning engine post-processing note: %s", l_err)

        # 8. Transition -> COMPLETED
        await self._transition_state(workflow_id, user_id, WorkflowState.COMPLETED, progress=1.0)
        yield {
            "event_type": "workflow_completed",
            "workflow_id": workflow_id,
            "result": {
                "summary": res_obj.summary,
                "status": res_obj.status,
                "confidence": res_obj.confidence,
                "tasks_completed": res_obj.tasks_completed,
                "tasks_failed": res_obj.tasks_failed
            }
        }

    async def _transition_state(
        self,
        workflow_id: str,
        user_id: str,
        target_state: WorkflowState,
        progress: Optional[float] = None
    ) -> None:
        wf = await self.repo.get_workflow(workflow_id, user_id)
        if not wf:
            return

        current = WorkflowState(wf.current_state)
        if not is_valid_transition(current, target_state):
            raise ValueError(f"Invalid workflow state transition: {current.value} -> {target_state.value}")

        await self.repo.update_workflow_state(
            workflow_id=workflow_id,
            user_id=user_id,
            state=target_state.value,
            progress=progress
        )
        await self.repo.create_event(
            workflow_id=workflow_id,
            event_type=f"workflow_state_{target_state.value.lower()}",
            payload={"previous_state": current.value, "new_state": target_state.value}
        )
