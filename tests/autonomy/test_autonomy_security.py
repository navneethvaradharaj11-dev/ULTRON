import pytest
from app.security.autonomy_security import AutonomySecurityValidator, AutonomySecurityError


def test_cross_tenant_rule_access_denied():
    with pytest.raises(AutonomySecurityError, match="ACCESS_DENIED"):
        AutonomySecurityValidator.validate_rule_access("user_alice", "user_bob")


def test_same_tenant_rule_access_allowed():
    # Should not raise exception
    AutonomySecurityValidator.validate_rule_access("user_alice", "user_alice")
