import pytest
from app.integrations.scope_manager import ScopeManager
from app.integrations.integration_policy import IntegrationPolicy


def test_scope_risk_mapping():
    assert ScopeManager.get_scope_risk("github", "READ_ISSUES") == "LOW"
    assert ScopeManager.get_scope_risk("github", "MERGE_PULL_REQUEST") == "HIGH"
    assert ScopeManager.requires_approval("github", "MERGE_PULL_REQUEST") is True


def test_integration_policy_evaluation():
    allowed, requires_approval, reason = IntegrationPolicy.evaluate_operation_policy(
        integration_id="github",
        operation_id="merge_pull_request",
        required_scopes=["MERGE_PULL_REQUEST"],
        granted_scopes=["MERGE_PULL_REQUEST"]
    )
    assert allowed is True
    assert requires_approval is True
