"""
test_event_consistency.py — Phase 2.5

Verifies the verify_event_consistency method detects malformed event
sequences and passes for well-formed ones.
"""
import pytest
from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.execution_engine import AgentExecutionEngine
from app.ai.model_manager import ModelManager
from app.engine.task_graph import TaskGraph, TaskNode


@pytest.mark.asyncio
async def test_consistent_events_after_full_execution(db_session):
    """A completed execution must report valid event consistency."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Calculate 3 * 3")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = TaskGraph(exec_rec.id, "Calculate 3 * 3")
    graph.add_task(TaskNode("t1", "calculate 3 * 3", assigned_agent="commander"))

    async for _ in engine.run_execution(exec_rec.id, graph, "test_user_id"):
        pass

    result = await repo.verify_event_consistency(exec_rec.id)
    assert result["valid"] is True, f"Expected valid event sequence. Issues: {result['issues']}"
    assert result["issues"] == []


@pytest.mark.asyncio
async def test_no_events_returns_invalid(db_session):
    """An execution with no events must be reported as invalid."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "No-event test")

    result = await repo.verify_event_consistency(exec_rec.id)
    assert result["valid"] is False
    assert any("No events" in issue for issue in result["issues"])


@pytest.mark.asyncio
async def test_missing_terminal_event_is_flagged(db_session):
    """An execution with only execution_started but no completion event is inconsistent."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Incomplete exec")

    # Manually insert just the start event (no terminal event)
    await repo.add_event(exec_rec.id, "execution_started", {"goal": "Incomplete exec"})
    await repo.add_event(exec_rec.id, "task_started", {"task_id": "t1"})
    # Deliberately omit task_completed and execution_completed

    result = await repo.verify_event_consistency(exec_rec.id)
    assert result["valid"] is False
    # Should flag both the unmatched started task and missing terminal event
    issues_text = " ".join(result["issues"])
    assert "t1" in issues_text or "terminal" in issues_text.lower()


@pytest.mark.asyncio
async def test_wrong_first_event_is_flagged(db_session):
    """An execution whose first event is not execution_started is inconsistent."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Wrong-order exec")

    await repo.add_event(exec_rec.id, "task_started", {"task_id": "t1"})
    await repo.add_event(exec_rec.id, "execution_started", {"goal": "wrong"})
    await repo.add_event(exec_rec.id, "execution_completed", {})

    result = await repo.verify_event_consistency(exec_rec.id)
    assert result["valid"] is False
    assert any("execution_started" in i for i in result["issues"])
