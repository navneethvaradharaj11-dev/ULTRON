import pytest
from app.database.migrations.phase10_unified_runtime import run_phase10_migrations
from app.core.ultron_core import UltronCore
from app.database.repositories.ultron_repo import UltronRepository
from app.security.unified_security import UnifiedSecurityGate, UnifiedSecurityError


@pytest.mark.asyncio
async def test_1_phase10_migration_idempotency():
    """Verify Phase 10 DDL migrations execute twice cleanly."""
    run_phase10_migrations()
    run_phase10_migrations()


@pytest.mark.asyncio
async def test_2_simple_command_execution(db_session):
    """Critical Test 1 — Simple Command ('Summarize this document')."""
    core = UltronCore(db_session)
    user_id = "user_p10_simple"

    res = await core.execute_unified_command(user_id, "Summarize this document")
    assert res["command_status"] == "WORKFLOW_CREATED"
    assert res["intent"]["intent_type"] == "KNOWLEDGE_QUERY"
    assert res["workflow_id"] is not None


@pytest.mark.asyncio
async def test_3_complex_command_execution(db_session):
    """Critical Test 2 — Complex Command ('Research this topic, create C implementation, and test it')."""
    core = UltronCore(db_session)
    user_id = "user_p10_complex"

    res = await core.execute_unified_command(
        user_id=user_id,
        message="Research quantum computing, create a C implementation for sorting, and run tests"
    )
    assert res["command_status"] == "WORKFLOW_CREATED"
    assert "research" in res["intent"]["required_capabilities"]
    assert "code" in res["intent"]["required_capabilities"]


@pytest.mark.asyncio
async def test_4_sensitive_action_requires_approval(db_session):
    """Critical Test 4 — Sensitive action triggers approval requirement."""
    core = UltronCore(db_session)
    user_id = "user_p10_approval"

    res = await core.execute_unified_command(user_id, "Submit external payment form")
    assert res["requires_approval"] is True


@pytest.mark.asyncio
async def test_5_cross_tenant_isolation(db_session):
    """Critical Test 7 — Multi-tenant isolation rejection."""
    user_a = "user_alice_p10"
    user_b = "user_bob_p10"

    with pytest.raises(UnifiedSecurityError, match="ACCESS_DENIED"):
        UnifiedSecurityGate.validate_tenant_access(user_a, user_b)


@pytest.mark.asyncio
async def test_6_monster_user_command_mission(db_session):
    """Part R Real-World Mission — 'ULTRON, analyze everything I have provided for this project...'."""
    core = UltronCore(db_session)
    repo = UltronRepository(db_session)
    user_id = "user_p10_monster"

    monster_command = (
        "ULTRON, analyze everything I have provided for this project. "
        "Understand the important requirements, use my previous project context where relevant, "
        "research anything missing, determine what needs to be done, create a plan, "
        "execute the work using the appropriate agents and tools, test the result safely, "
        "fix problems if necessary, verify everything, save the useful artifact, "
        "and give me a concise explanation of what you did."
    )

    res = await core.execute_unified_command(user_id, monster_command)
    assert res["command_status"] == "WORKFLOW_CREATED"
    assert res["workflow_id"] is not None

    # Record activity in timeline
    act = await repo.record_activity(
        user_id=user_id,
        activity_type="MONSTER_MISSION_STARTED",
        title="Monster Command Executed",
        workflow_id=res["workflow_id"]
    )
    assert act.id is not None
