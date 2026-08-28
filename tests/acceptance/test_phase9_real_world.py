import pytest
from app.database.migrations.phase9_autonomy import run_phase9_migrations
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.autonomy.autonomy_manager import AutonomyManager
from app.autonomy.contracts import AutonomyLevel, DecisionType
from app.autonomy.cooldown import CooldownManager
from app.autonomy.deduplication import DeduplicationManager
from app.security.autonomy_security import AutonomySecurityValidator, AutonomySecurityError
from app.intelligence.secret_detector import SecretDetector


@pytest.mark.asyncio
async def test_1_database_migration_idempotency():
    """Verify Phase 9 DDL migrations run twice cleanly."""
    run_phase9_migrations()
    run_phase9_migrations()


@pytest.mark.asyncio
async def test_2_scheduled_rule_end_to_end(db_session):
    """Verify scheduled rule creation, trigger handling, decision reasoning, and workflow creation."""
    manager = AutonomyManager(db_session)
    user_id = "user_p9_scheduled"

    rule = await manager.create_rule(
        user_id=user_id,
        name="Nightly Workspace Check",
        goal_template="Check workspace for important code changes and compute 2 + 2",
        trigger_type="SCHEDULE",
        autonomy_level="LEVEL_2",
        cooldown_seconds=1
    )

    res = await manager.handle_trigger_event(
        user_id=user_id,
        rule_id=rule["rule_id"],
        event_type="SCHEDULE",
        source="cron_trigger",
        payload={"scheduled_time": "19:00"}
    )

    assert res["status"] == "PROCESSED"
    assert res["decision_type"] == "START_WORKFLOW"
    assert res["execution"]["action"] == "WORKFLOW_EXECUTED"


@pytest.mark.asyncio
async def test_3_disabled_rule_does_not_execute(db_session):
    """Verify disabled rules do not execute when triggered."""
    manager = AutonomyManager(db_session)
    repo = AutonomyRepository(db_session)
    user_id = "user_p9_disabled"

    rule = await manager.create_rule(
        user_id=user_id,
        name="Disabled Rule Test",
        goal_template="Disabled goal",
        trigger_type="SCHEDULE"
    )
    rule_id = rule["rule_id"]

    await repo.toggle_rule_enabled(rule_id, user_id, False)

    res = await manager.handle_trigger_event(
        user_id=user_id,
        rule_id=rule_id,
        event_type="SCHEDULE",
        source="cron",
        payload={}
    )
    assert res["status"] == "DISABLED"


@pytest.mark.asyncio
async def test_4_cooldown_window_enforcement(db_session):
    """Verify rapid repeated triggers are suppressed during cooldown."""
    manager = AutonomyManager(db_session)
    user_id = "user_p9_cooldown"

    rule = await manager.create_rule(
        user_id=user_id,
        name="Cooldown Rule",
        goal_template="Cooldown test",
        trigger_type="INTERVAL",
        cooldown_seconds=600
    )
    rule_id = rule["rule_id"]

    res1 = await manager.handle_trigger_event(user_id, rule_id, "INTERVAL", "timer", {"tick": 1})
    assert res1["status"] == "PROCESSED"

    res2 = await manager.handle_trigger_event(user_id, rule_id, "INTERVAL", "timer", {"tick": 2})
    assert res2["status"] == "COOLDOWN_ACTIVE"


@pytest.mark.asyncio
async def test_5_event_deduplication(db_session):
    """Verify identical duplicate events are ignored."""
    user_id = "user_p9_dedup"
    key1 = DeduplicationManager.generate_key(user_id, "WEB_CHANGE", "site_monitor", "Price=100")
    key2 = DeduplicationManager.generate_key(user_id, "WEB_CHANGE", "site_monitor", "Price=100")

    assert DeduplicationManager.is_duplicate(key1) is False
    assert DeduplicationManager.is_duplicate(key2) is True


@pytest.mark.asyncio
async def test_6_level_3_approval_required(db_session):
    """Verify Level 3 sensitive actions trigger REQUIRE_APPROVAL."""
    manager = AutonomyManager(db_session)
    user_id = "user_p9_approval"

    rule = await manager.create_rule(
        user_id=user_id,
        name="Sensitive External Action",
        goal_template="Submit external form",
        trigger_type="WEB_CHANGE",
        autonomy_level="LEVEL_3",
        cooldown_seconds=1
    )

    res = await manager.handle_trigger_event(
        user_id=user_id,
        rule_id=rule["rule_id"],
        event_type="WEB_CHANGE",
        source="website_monitor",
        payload={"url": "https://example.com"}
    )
    assert res["status"] == "PROCESSED"
    assert res["decision_type"] == "REQUIRE_APPROVAL"
    assert res["execution"]["action"] == "REQUIRE_APPROVAL"


@pytest.mark.asyncio
async def test_7_cross_tenant_isolation_enforcement(db_session):
    """Verify User A cannot access or trigger User B's autonomy rules."""
    manager = AutonomyManager(db_session)
    user_a = "user_a_auto"
    user_b = "user_b_auto"

    rule_a = await manager.create_rule(user_a, "User A Rule", "Goal A", "SCHEDULE")
    rule_id_a = rule_a["rule_id"]

    # User B attempts to access or trigger User A's rule
    with pytest.raises(ValueError, match="not found"):
        await manager.handle_trigger_event(user_b, rule_id_a, "SCHEDULE", "hack", {})

    with pytest.raises(AutonomySecurityError, match="ACCESS_DENIED"):
        AutonomySecurityValidator.validate_rule_access(user_a, user_b)


@pytest.mark.asyncio
async def test_8_secret_sanitization_in_notifications():
    """Verify secret detector sanitizes raw credentials in notification titles and bodies."""
    secret_text = "Alert: API_KEY=FAKE_SECRET_KEY_99999 leak detected"
    sanitized = SecretDetector.sanitize_text(secret_text)
    assert "FAKE_SECRET_KEY_99999" not in sanitized
    assert "[REDACTED_" in sanitized
