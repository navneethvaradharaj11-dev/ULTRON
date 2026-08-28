import pytest
from app.security.unified_security import UnifiedSecurityGate, UnifiedSecurityError
from app.security.browser_security import BrowserSecurity
from app.security.computer_security import ComputerSecurityValidator
from app.security.token_blacklist import token_blacklist
from app.core.resource_budget import ResourceBudgetTracker, ResourceBudgetExceededError


def test_1_unauthorized_tenant_access_denied():
    with pytest.raises(UnifiedSecurityError, match="ACCESS_DENIED"):
        UnifiedSecurityGate.validate_tenant_access("user_alice", "user_bob")


def test_2_ssrf_browser_protection():
    assert not BrowserSecurity.validate_url("http://127.0.0.1:8000/admin")
    assert not BrowserSecurity.validate_url("http://169.254.169.254/latest/meta-data")
    assert BrowserSecurity.validate_url("https://example.com/docs")


def test_3_visual_perception_low_confidence_rejected():
    validator = ComputerSecurityValidator()
    # confidence = 0.50 (< 0.60 threshold)
    allowed, status, reason = validator.validate_action_safety(
        session=None,
        action_type="click",
        target={"x": 10, "y": 10},
        parameters={"x": 10, "y": 10},
        confidence=0.50
    )
    assert not allowed
    assert "FORBIDDEN" in status


def test_4_token_blacklist_revocation():
    token_blacklist.revoke_token("test_revoked_jwt_token_123")
    assert token_blacklist.is_token_revoked("test_revoked_jwt_token_123")


def test_5_resource_budget_limit_enforcement():
    tracker = ResourceBudgetTracker(max_tool_calls=1)
    tracker.record_tool_call()
    with pytest.raises(ResourceBudgetExceededError):
        tracker.record_tool_call()
