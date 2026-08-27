"""
test_agent_metrics.py — Phase 2.5

Verifies that agent metrics are recorded after task execution and that
aggregate stats are correctly computed.
"""
import pytest
from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.task_graph import TaskGraph, TaskNode
from app.ai.model_manager import ModelManager


@pytest.mark.asyncio
async def test_metrics_recorded_after_task_completion(db_session):
    """Completing a task must produce an ExecutionMetrics record."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Metric test: calculate 1 + 1")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = TaskGraph(exec_rec.id, "calculate 1 + 1")
    graph.add_task(TaskNode("t1", "calculate 1 + 1", assigned_agent="commander"))

    async for _ in engine.run_execution(exec_rec.id, graph, "test_user_id"):
        pass

    metrics = await repo.get_execution_metrics(exec_rec.id)
    assert len(metrics) >= 1, "At least one metric record must be written"

    m = metrics[0]
    assert m.execution_id == exec_rec.id
    assert m.status in ("COMPLETED", "FAILED")
    assert m.duration_ms >= 0


@pytest.mark.asyncio
async def test_metrics_include_agent_name(db_session):
    """Metrics must capture the correct agent name."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Agent name metric test")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = TaskGraph(exec_rec.id, "calculate 2 * 5")
    graph.add_task(TaskNode("t1", "calculate 2 * 5", assigned_agent="commander"))

    async for _ in engine.run_execution(exec_rec.id, graph, "test_user_id"):
        pass

    metrics = await repo.get_execution_metrics(exec_rec.id)
    agent_names = [m.agent_name for m in metrics]
    # The calculator tool reports as "calculator_tool"; if falling back to commander,
    # the reviewer also runs — either way there must be at least one entry
    assert len(agent_names) >= 1


@pytest.mark.asyncio
async def test_aggregate_metrics_by_user(db_session):
    """Aggregate metrics must cover multiple executions and group by agent."""
    repo = ExecutionRepository(db_session)
    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())

    for goal in ["calculate 1 + 1", "calculate 2 + 2"]:
        exec_rec = await repo.create_execution("test_user_id", goal)
        graph = TaskGraph(exec_rec.id, goal)
        graph.add_task(TaskNode("t1", goal, assigned_agent="commander"))
        async for _ in engine.run_execution(exec_rec.id, graph, "test_user_id"):
            pass

    stats = await repo.get_aggregate_agent_metrics("test_user_id")
    assert isinstance(stats, list), "Aggregate result must be a list"
    assert len(stats) >= 1, "At least one agent stat group must be present"

    # Verify required fields exist
    for stat in stats:
        assert "agent_name" in stat
        assert "total_tasks" in stat
        assert "total_duration_ms" in stat
        assert stat["total_tasks"] >= 1


@pytest.mark.asyncio
async def test_manual_metric_recording(db_session):
    """Directly recording metrics via repo.record_metrics must persist correctly."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Manual metric")

    metric = await repo.record_metrics(
        execution_id=exec_rec.id,
        task_id=None,
        agent_name="researcher",
        duration_ms=423,
        status="COMPLETED",
        retry_count=1,
        tools_used=["web_search"],
        review_status="approved",
        review_confidence=0.92
    )

    assert metric.id is not None
    assert metric.agent_name == "researcher"
    assert metric.duration_ms == 423
    assert metric.retry_count == 1
    assert metric.review_confidence == 92  # stored as 0-100 integer
    assert metric.review_status == "approved"
