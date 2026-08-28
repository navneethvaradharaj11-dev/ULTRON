import pytest
from app.orchestration.agent_coordinator import AgentCoordinator

@pytest.mark.asyncio
async def test_agent_coordinator_execution(db_session):
    coordinator = AgentCoordinator(db_session)
    res = await coordinator.execute_task(
        task_id="t1",
        goal="Calculate 10 + 20",
        assigned_agent="commander",
        user_id="user_test",
        execution_id="exec_1"
    )
    assert res["status"] == "COMPLETED"
    assert res["task_id"] == "t1"
