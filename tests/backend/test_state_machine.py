"""
test_state_machine.py — Phase 2.5

Verify that the Execution and ExecutionTask state machines
accept valid transitions and guard against illegal ones.
"""
import pytest
from app.database.repositories.execution_repo import (
    ExecutionRepository,
    validate_execution_transition,
    validate_task_transition,
)


# ---------------------------------------------------------------------------
# Pure function tests (no DB needed)
# ---------------------------------------------------------------------------

def test_execution_valid_transitions():
    assert validate_execution_transition("PENDING", "RUNNING") is True
    assert validate_execution_transition("RUNNING", "COMPLETED") is True
    assert validate_execution_transition("RUNNING", "FAILED") is True
    assert validate_execution_transition("RUNNING", "CANCELLED") is True
    assert validate_execution_transition("PENDING", "CANCELLED") is True


def test_execution_invalid_transitions():
    assert validate_execution_transition("COMPLETED", "RUNNING") is False
    assert validate_execution_transition("FAILED", "RUNNING") is False
    assert validate_execution_transition("CANCELLED", "RUNNING") is False
    assert validate_execution_transition("COMPLETED", "CANCELLED") is False
    assert validate_execution_transition("PENDING", "COMPLETED") is False  # must go RUNNING first


def test_task_valid_transitions():
    assert validate_task_transition("PENDING", "RUNNING") is True
    assert validate_task_transition("RUNNING", "COMPLETED") is True
    assert validate_task_transition("RUNNING", "FAILED") is True
    assert validate_task_transition("RUNNING", "REQUIRES_APPROVAL") is True
    assert validate_task_transition("RUNNING", "WAITING") is True
    assert validate_task_transition("WAITING", "RUNNING") is True
    assert validate_task_transition("REQUIRES_APPROVAL", "RUNNING") is True
    assert validate_task_transition("PENDING", "CANCELLED") is True


def test_task_invalid_transitions():
    assert validate_task_transition("COMPLETED", "RUNNING") is False
    assert validate_task_transition("FAILED", "RUNNING") is False
    assert validate_task_transition("CANCELLED", "PENDING") is False
    assert validate_task_transition("COMPLETED", "FAILED") is False


# ---------------------------------------------------------------------------
# DB-backed state machine enforcement
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_execution_illegal_transition_is_silently_skipped(db_session):
    """An illegal transition (COMPLETED → RUNNING) must be a no-op, not an exception."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "State test")

    # Drive to COMPLETED
    await repo.update_execution_status(exec_rec.id, "RUNNING")
    await repo.update_execution_status(exec_rec.id, "COMPLETED")

    # Attempt illegal back-transition
    result = await repo.update_execution_status(exec_rec.id, "RUNNING")
    assert result is not None
    assert result.status == "COMPLETED", "Status must stay COMPLETED after illegal transition"


@pytest.mark.asyncio
async def test_task_illegal_transition_is_silently_skipped(db_session):
    """An illegal task transition (COMPLETED → RUNNING) must not change the status."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Task state test")
    task = await repo.create_execution_task(exec_rec.id, "Do something", "commander")

    await repo.update_task_status(task.id, "RUNNING")
    await repo.update_task_status(task.id, "COMPLETED", output_json={"done": True})

    # Attempt illegal back-transition
    result = await repo.update_task_status(task.id, "RUNNING")
    assert result is not None
    assert result.status == "COMPLETED", "Task status must stay COMPLETED after illegal transition"


@pytest.mark.asyncio
async def test_force_flag_bypasses_state_machine(db_session):
    """force=True must allow a transition that would otherwise be rejected."""
    repo = ExecutionRepository(db_session)
    exec_rec = await repo.create_execution("test_user_id", "Force override test")

    await repo.update_execution_status(exec_rec.id, "RUNNING")
    await repo.update_execution_status(exec_rec.id, "COMPLETED")

    # Force back to RUNNING (e.g., admin override)
    result = await repo.update_execution_status(exec_rec.id, "RUNNING", force=True)
    assert result.status == "RUNNING"
