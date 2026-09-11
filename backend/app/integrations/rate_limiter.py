import time
import logging
from typing import Dict, Tuple

logger = logging.getLogger("ULTRON.Integrations.RateLimiter")


class IntegrationRateLimitedError(Exception):
    """Exception raised when an integration operation rate limit is exceeded."""
    pass


class IntegrationRateLimiter:
    """Tracks rate limits per user, integration, and operation."""

    def __init__(self, max_requests_per_minute: int = 30):
        self.max_requests_per_minute = max_requests_per_minute
        self._counts: Dict[str, Tuple[int, float]] = {}

    def check_rate_limit(self, user_id: str, integration_id: str, operation_id: str) -> None:
        key = f"{user_id}:{integration_id.lower()}:{operation_id.lower()}"
        now = time.time()
        count, window_start = self._counts.get(key, (0, now))

        if now - window_start > 60.0:
            self._counts[key] = (1, now)
            return

        if count >= self.max_requests_per_minute:
            raise IntegrationRateLimitedError(
                f"RATE_LIMITED: Operation '{operation_id}' on '{integration_id}' exceeded limit of {self.max_requests_per_minute} req/min."
            )

        self._counts[key] = (count + 1, window_start)


# Global singleton instance
integration_rate_limiter = IntegrationRateLimiter()
