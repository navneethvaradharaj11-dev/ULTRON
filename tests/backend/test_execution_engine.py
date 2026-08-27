import pytest
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.execution_engine import AgentExecutionEngine
from app.database.repositories.execution_repo import ExecutionRepository
from app.ai.model_manager import ModelManager


@pytest.mark.asyncio
async def test_execution_engine_run(db_session):
    repo = ExecutionRepository(db_session)
    exec_record = await repo.create_execution("test_user_id", "Calculate 10 + 20")

    engine = AgentExecutionEngine(db=db_session, model_manager=ModelManager())
    graph = TaskGraph(exec_record.id, "Calculate 10 + 20")
    graph.add_task(TaskNode("t1", "calculate 10 + 20", assigned_agent="commander"))

    events = []
    async for event in engine.run_execution(exec_record.id, graph, "test_user_id"):
        events.append(event)

    assert len(events) >= 5
    event_types = [e["event_type"] for e in events]
    assert "execution_started" in event_types
    assert "plan_created" in event_types
    assert "execution_completed" in event_types
    assert graph.is_complete() is True
