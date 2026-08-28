from enum import Enum
from typing import Set

class WorkflowState(str, Enum):
    CREATED = "CREATED"
    UNDERSTANDING = "UNDERSTANDING"
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RECOVERING = "RECOVERING"
    REPLANNING = "REPLANNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

# Valid state transitions
VALID_TRANSITIONS: dict[WorkflowState, Set[WorkflowState]] = {
    WorkflowState.CREATED: {WorkflowState.UNDERSTANDING, WorkflowState.CANCELLED, WorkflowState.FAILED},
    WorkflowState.UNDERSTANDING: {WorkflowState.PLANNING, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.PLANNING: {WorkflowState.READY, WorkflowState.WAITING_APPROVAL, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.WAITING_APPROVAL: {WorkflowState.RUNNING, WorkflowState.READY, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.READY: {WorkflowState.RUNNING, WorkflowState.PAUSED, WorkflowState.CANCELLED, WorkflowState.FAILED},
    WorkflowState.RUNNING: {WorkflowState.VERIFYING, WorkflowState.WAITING_APPROVAL, WorkflowState.PAUSED, WorkflowState.RECOVERING, WorkflowState.REPLANNING, WorkflowState.FAILED, WorkflowState.CANCELLED, WorkflowState.COMPLETED},
    WorkflowState.PAUSED: {WorkflowState.RUNNING, WorkflowState.CANCELLED},
    WorkflowState.RECOVERING: {WorkflowState.RUNNING, WorkflowState.REPLANNING, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.REPLANNING: {WorkflowState.RUNNING, WorkflowState.READY, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.VERIFYING: {WorkflowState.COMPLETED, WorkflowState.RECOVERING, WorkflowState.REPLANNING, WorkflowState.FAILED, WorkflowState.CANCELLED},
    WorkflowState.COMPLETED: set(),
    WorkflowState.FAILED: set(),
    WorkflowState.CANCELLED: set()
}

def is_valid_transition(current: WorkflowState, next_state: WorkflowState) -> bool:
    """Validate if transition from current to next_state is permitted."""
    if current == next_state:
        return True
    allowed = VALID_TRANSITIONS.get(current, set())
    return next_state in allowed
