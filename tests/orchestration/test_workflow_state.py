import pytest
from app.orchestration.workflow_state import WorkflowState, is_valid_transition

def test_workflow_state_valid_transitions():
    assert is_valid_transition(WorkflowState.CREATED, WorkflowState.UNDERSTANDING) is True
    assert is_valid_transition(WorkflowState.UNDERSTANDING, WorkflowState.PLANNING) is True
    assert is_valid_transition(WorkflowState.PLANNING, WorkflowState.READY) is True
    assert is_valid_transition(WorkflowState.READY, WorkflowState.RUNNING) is True
    assert is_valid_transition(WorkflowState.RUNNING, WorkflowState.VERIFYING) is True
    assert is_valid_transition(WorkflowState.VERIFYING, WorkflowState.COMPLETED) is True

def test_workflow_state_invalid_transitions():
    assert is_valid_transition(WorkflowState.CREATED, WorkflowState.COMPLETED) is False
    assert is_valid_transition(WorkflowState.COMPLETED, WorkflowState.RUNNING) is False
    assert is_valid_transition(WorkflowState.FAILED, WorkflowState.RUNNING) is False
