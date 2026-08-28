import pytest
from app.engine.execution_engine import AgentExecutionEngine
from app.engine.task_graph import TaskGraph, TaskNode
from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.strategy_engine import StrategyEngine
from app.database.repositories.execution_repo import ExecutionRepository

@pytest.mark.asyncio
async def test_intelligence_e2e_pipeline(db_session):
    user_id = "test_e2e_user"
    
    # 1. Store initial preference memory
    mem_engine = MemoryEngine(db_session)
    await mem_engine.add_memory(
        user_id=user_id,
        content="Prefer fast math calculation strategy",
        memory_type="PREFERENCE"
    )

    # 2. Setup execution in DB
    exec_repo = ExecutionRepository(db_session)
    execution = await exec_repo.create_execution(user_id=user_id, goal="Calculate 100 * 25")

    # 3. Create TaskGraph
    graph = TaskGraph(execution.id, execution.goal)
    node = TaskNode(
        task_id="task_calc_1",
        goal="Calculate 100 * 25",
        assigned_agent="commander"
    )
    graph.add_task(node)

    # 4. Run Execution Engine
    engine = AgentExecutionEngine(db_session)
    events = []
    async for evt in engine.run_execution(execution.id, graph, user_id=user_id):
        events.append(evt)

    event_types = [e["event_type"] for e in events]
    assert "execution_started" in event_types
    assert "memory_retrieval_started" in event_types
    assert "memory_retrieved" in event_types
    assert "context_built" in event_types
    assert "strategy_selected" in event_types
    assert "execution_completed" in event_types
    assert "learning_started" in event_types
    assert "learning_completed" in event_types

    # 5. Verify strategy was learned and stored
    strat_engine = StrategyEngine(db_session)
    best_strat = await strat_engine.best_strategy("mathematical_computation")
    assert best_strat is not None
    assert best_strat["goal_type"] == "mathematical_computation"
