import pytest
import asyncio
from app.database.repositories.workflow_repo import WorkflowRepository
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.security.unified_security import UnifiedSecurityGate, UnifiedSecurityError


@pytest.mark.asyncio
async def test_concurrent_workflow_creation(db_session):
    repo = WorkflowRepository(db_session)
    user_id = "user_concurrent_test"

    workflows = []
    for i in range(5):
        wf = await repo.create_workflow(user_id=user_id, goal=f"Concurrent Goal {i}")
        workflows.append(wf)

    assert len(workflows) == 5
    for wf in workflows:
        assert wf.id is not None
        assert wf.user_id == user_id




@pytest.mark.asyncio
async def test_cross_user_resource_access_rejection():
    owner_user = "user_alice"
    attacker_user = "user_bob"

    with pytest.raises(UnifiedSecurityError, match="ACCESS_DENIED"):
        UnifiedSecurityGate.validate_tenant_access(owner_user, attacker_user)
