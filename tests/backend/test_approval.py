import pytest
from app.engine.approval_manager import ApprovalManager
from app.database.repositories.execution_repo import ExecutionRepository


@pytest.mark.asyncio
async def test_approval_workflow(db_session):
    repo = ExecutionRepository(db_session)
    exec_item = await repo.create_execution("test_user_id", "Delete sensitive file")
    task_item = await repo.create_execution_task(exec_item.id, "delete file", "coder")

    manager = ApprovalManager(db_session)
    appr = await manager.create_request(exec_item.id, task_item.id, "filesystem_write", {"file_path": "sandbox/clean.txt"})
    assert appr.status == "pending"

    res = await manager.submit_response(appr.id, "approved")
    assert res.status == "approved"
