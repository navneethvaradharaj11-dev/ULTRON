import pytest
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.execution_engine import AgentExecutionEngine
from app.database.repositories.execution_repo import ExecutionRepository
from app.database.repositories.code_repo import CodeRepository
from app.database.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_deterministic_code_execution_e2e(db_session):
    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("c_coder_dev", "c_coder@ultron.ai", "pass12345")

    exec_repo = ExecutionRepository(db_session)

    execution = await exec_repo.create_execution(
        user_id=user.id,
        goal="Create a C program that finds the maximum value in an array, compile it, test it with multiple inputs, fix any errors, and provide the final result."
    )

    # Build Task Graph
    graph = TaskGraph(execution.id, execution.goal)
    
    t1 = TaskNode("t1", "Analyze requirements for C array max value program", assigned_agent="planner")
    t2 = TaskNode("t2", "Create main.c implementation", assigned_agent="coder", dependencies=["t1"])
    t3 = TaskNode("t3", "Compile main.c", assigned_agent="coder", dependencies=["t2"])
    t4 = TaskNode("t4", "Execute C array max program and verify output", assigned_agent="coder", dependencies=["t3"])
    t5 = TaskNode("t5", "Review code, compilation, and execution results", assigned_agent="reviewer", dependencies=["t4"])

    for node in [t1, t2, t3, t4, t5]:
        graph.add_task(node)

    engine = AgentExecutionEngine(db_session)
    events = []
    async for evt in engine.run_execution(execution.id, graph, user.id):
        events.append(evt)

    # Verification
    event_types = [e["event_type"] for e in events]
    assert "execution_started" in event_types
    assert "plan_created" in event_types
    assert "task_started" in event_types
    assert "execution_completed" in event_types

    # Database state verification
    exec_db = await exec_repo.get_execution_by_id(execution.id)
    assert exec_db.status == "COMPLETED"

    # Verify task statuses
    tasks_db = await exec_repo.get_execution_tasks(execution.id)
    for t in tasks_db:
        assert t.status == "COMPLETED"
