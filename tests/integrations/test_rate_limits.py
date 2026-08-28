import pytest
from app.integrations.rate_limiter import IntegrationRateLimiter, IntegrationRateLimitedError


def test_rate_limiter_exceeded():
    limiter = IntegrationRateLimiter(max_requests_per_minute=2)
    limiter.check_rate_limit("user1", "github", "list_issues")
    limiter.check_rate_limit("user1", "github", "list_issues")

    with pytest.raises(IntegrationRateLimitedError, match="RATE_LIMITED"):
        limiter.check_rate_limit("user1", "github", "list_issues")
