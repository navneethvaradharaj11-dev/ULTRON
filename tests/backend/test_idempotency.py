"""
test_idempotency.py — Phase 2.5

Verify that supplying the same idempotency_key to create_execution
returns the existing record instead of creating a duplicate.
"""
import pytest
from app.database.repositories.execution_repo import ExecutionRepository


@pytest.mark.asyncio
async def test_idempotency_key_returns_existing(db_session):
    """Submitting the same idempotency_key twice must return the same execution."""
    repo = ExecutionRepository(db_session)

    key = "idem-key-abc123"
    exec1 = await repo.create_execution("test_user_id", "Goal A", idempotency_key=key)
    exec2 = await repo.create_execution("test_user_id", "Goal B", idempotency_key=key)

    assert exec1.id == exec2.id, "Duplicate key must return the original execution"
    assert exec2.goal == "Goal A", "Goal must not be overwritten by second call"


@pytest.mark.asyncio
async def test_idempotency_key_none_creates_new(db_session):
    """Without an idempotency_key, every call creates a distinct execution."""
    repo = ExecutionRepository(db_session)

    exec1 = await repo.create_execution("test_user_id", "Goal X")
    exec2 = await repo.create_execution("test_user_id", "Goal Y")

    assert exec1.id != exec2.id, "Without key, two distinct executions must be created"


@pytest.mark.asyncio
async def test_different_idempotency_keys_create_separate_executions(db_session):
    """Different keys must result in separate executions."""
    repo = ExecutionRepository(db_session)

    e1 = await repo.create_execution("test_user_id", "Task 1", idempotency_key="key-001")
    e2 = await repo.create_execution("test_user_id", "Task 2", idempotency_key="key-002")

    assert e1.id != e2.id


@pytest.mark.asyncio
async def test_idempotency_key_stored_on_execution(db_session):
    """The idempotency_key must be persisted on the record."""
    repo = ExecutionRepository(db_session)

    key = "stored-key-xyz"
    exec1 = await repo.create_execution("test_user_id", "Some goal", idempotency_key=key)
    fetched = await repo.get_execution_by_id(exec1.id)

    assert fetched is not None
    assert fetched.idempotency_key == key
