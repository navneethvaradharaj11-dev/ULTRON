"""
test_crash_recovery.py — Phase 2.5

Verifies that an execution which was partially completed (e.g., process
crashed mid-run leaving a task in RUNNING state) can be resumed correctly.

The test simulates a crash by:
1. Creating an execution and persisting some tasks
2. Manually marking one task COMPLETED and leaving another RUNNING
3. Calling rebuild_graph_from_db and verifying the engine resumes correctly
"""
import pytest
from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.contracts import TaskStatus
from app.engine.task_graph import TaskGraph, TaskNode
from app.ai.model_manager import ModelManager


@pytest.mark.asyncio
async def test_running_tasks_reset_to_pending_on_resume(db_session):
    """RUNNING tasks (orphaned by a crash) must be reset to PENDING before resumption."""
    repo = ExecutionRepository(db_session)

    # Simulate partial execution: execution RUNNING, task_1 COMPLETED, task_2 stuck in RUNNING
    exec_rec = await repo.create_execution("test_user_id", "Two-step research")
    await repo.update_execution_status(exec_rec.id, "RUNNING")

    task1 = await repo.create_execution_task(exec_rec.id, "Research topic", "researcher")
    task2 = await repo.create_execution_task(exec_rec.id, "Synthesize results", "reviewer",
                                              dependencies=[task1.id])

    # task1 completed before crash
    await repo.update_task_status(task1.id, "RUNNING")
    await repo.update_task_status(task1.id, "COMPLETED", output_json={"findings": "AI trends"})

    # task2 was RUNNING when process died
    await repo.update_task_status(task2.id, "RUNNING")

    # --- Resume ---
    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = await engine.rebuild_graph_from_db(exec_rec.id)

    assert graph is not None, "rebuild_graph_from_db must return a graph for a RUNNING execution"

    # task1 should be COMPLETED in the graph
    t1_node = graph.get_task(task1.id)
    assert t1_node is not None
    assert t1_node.status == TaskStatus.COMPLETED, "Completed task must carry over as COMPLETED"

    # task2 must be back to PENDING (was RUNNING → reset)
    t2_node = graph.get_task(task2.id)
    assert t2_node is not None
    assert t2_node.status == TaskStatus.PENDING, "Orphaned RUNNING task must be reset to PENDING"


@pytest.mark.asyncio
async def test_rebuild_graph_terminal_execution_returns_none(db_session):
    """rebuild_graph_from_db must return None for a terminal (COMPLETED) execution."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Already done")
    await repo.update_execution_status(exec_rec.id, "RUNNING")
    await repo.update_execution_status(exec_rec.id, "COMPLETED")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = await engine.rebuild_graph_from_db(exec_rec.id)

    assert graph is None, "Terminal execution must not be resumable"


@pytest.mark.asyncio
async def test_full_resume_executes_pending_tasks(db_session):
    """After rebuild, running the engine must complete all remaining PENDING tasks."""
    repo = ExecutionRepository(db_session)

    exec_rec = await repo.create_execution("test_user_id", "Calculate 5 + 5")
    await repo.update_execution_status(exec_rec.id, "RUNNING")

    # Persist one task as though we're resuming from the beginning
    t1 = await repo.create_execution_task(exec_rec.id, "calculate 5 + 5", "commander")
    # Simulate crash: it was RUNNING
    await repo.update_task_status(t1.id, "RUNNING")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = await engine.rebuild_graph_from_db(exec_rec.id)

    assert graph is not None
    events = []
    async for event in engine.run_execution(exec_rec.id, graph, "test_user_id"):
        events.append(event)

    event_types = [e["event_type"] for e in events]
    assert "execution_completed" in event_types, "Resume must complete the execution"

    exec_final = await repo.get_execution_by_id(exec_rec.id)
    assert exec_final.status == "COMPLETED"
