import pytest
from app.security.orchestration_security import OrchestrationSecurity, OrchestrationSecurityError

def test_tenant_ownership_enforcement():
    sec = OrchestrationSecurity()
    # Same user passes
    sec.validate_tenant_ownership("user_A", "user_A")

    # Mismatched user raises OrchestrationSecurityError
    with pytest.raises(OrchestrationSecurityError):
        sec.validate_tenant_ownership("user_A", "user_B")

def test_quota_limits():
    sec = OrchestrationSecurity()
    
    with pytest.raises(OrchestrationSecurityError):
        sec.check_task_quota(50)

    with pytest.raises(OrchestrationSecurityError):
        sec.check_retry_quota(3)

    with pytest.raises(OrchestrationSecurityError):
        sec.check_replan_quota(3)
