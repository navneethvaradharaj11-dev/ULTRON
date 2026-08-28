import pytest
from app.orchestration.orchestrator import WorkflowOrchestrator
from app.database.repositories.workflow_repo import WorkflowRepository

@pytest.mark.asyncio
async def test_full_autonomous_workflow_e2e_pipeline(db_session):
    user_id = "test_wf_user"
    goal = "Calculate mathematical expression 50 * 4"

    orchestrator = WorkflowOrchestrator(db_session)
    wf = await orchestrator.create_workflow(user_id=user_id, goal=goal)

    assert wf.workflow_id is not None
    assert wf.current_state.value == "CREATED"

    events = []
    async for evt in orchestrator.execute_workflow(wf.workflow_id, user_id):
        events.append(evt)

    event_types = [e["event_type"] for e in events]
    assert "workflow_understanding" in event_types
    assert "workflow_memory_lookup" in event_types
    assert "workflow_strategy_selected" in event_types
    assert "workflow_plan_created" in event_types
    assert "workflow_checkpoint_created" in event_types
    assert "workflow_started" in event_types
    assert "workflow_step_started" in event_types
    assert "workflow_step_completed" in event_types
    assert "workflow_verification_started" in event_types
    assert "workflow_verification_completed" in event_types
    assert "workflow_completed" in event_types

    # Verify database persistence
    repo = WorkflowRepository(db_session)
    wf_saved = await repo.get_workflow(wf.workflow_id, user_id)
    assert wf_saved is not None
    assert wf_saved.current_state == "COMPLETED"
    assert wf_saved.progress == 1.0

    res_saved = await repo.get_result(wf.workflow_id, user_id)
    assert res_saved is not None
    assert res_saved.status == "COMPLETED"
