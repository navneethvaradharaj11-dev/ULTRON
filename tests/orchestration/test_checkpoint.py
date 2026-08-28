import pytest
from app.orchestration.checkpoint_manager import CheckpointManager

@pytest.mark.asyncio
async def test_checkpoint_save_and_load(db_session):
    mgr = CheckpointManager(db_session)
    user_id = "user_cp"
    
    # Save checkpoint via repo
    from app.database.repositories.workflow_repo import WorkflowRepository
    repo = WorkflowRepository(db_session)
    wf = await repo.create_workflow(user_id=user_id, goal="Checkpoint test")

    await mgr.save_checkpoint(
        workflow_id=wf.id,
        checkpoint_name="plan_validated",
        state_snapshot={"completed_tasks": ["t1"]}
    )

    loaded = await mgr.load_latest_checkpoint(wf.id, user_id)
    assert loaded is not None
    assert loaded["completed_tasks"] == ["t1"]
