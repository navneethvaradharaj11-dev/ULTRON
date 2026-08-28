import pytest
from app.intelligence.learning_engine import LearningEngine

@pytest.mark.asyncio
async def test_learning_engine_process_execution(db_session):
    engine = LearningEngine(db_session)
    res = await engine.process_execution_result(
        user_id="user_l",
        execution_id="exec_123",
        goal="Calculate mathematical expression and store result",
        plan=[{"id": "t1", "goal": "calculate"}],
        tasks_results=[{"task_id": "t1", "agent": "coder", "status": "COMPLETED", "duration_ms": 500}],
        overall_success=True,
        duration_ms=500
    )

    assert res["episodic_id"] is not None
    assert res["pattern_detected"] is not None
    assert res["goal_type"] == "mathematical_computation"
