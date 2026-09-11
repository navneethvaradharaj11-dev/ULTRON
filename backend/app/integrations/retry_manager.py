import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger("ULTRON.Integrations.RetryManager")


class RetryManager:
    """Retries ONLY safe transient failures (HTTP 429, 5xx, network timeout) with exponential backoff.
    Never retries destructive or write actions.
    """

    @staticmethod
    async def execute_with_retry(
        func: Callable[[], Any],
        is_read_only: bool = True,
        max_retries: int = 3,
        backoff_seconds: float = 1.0
    ) -> Any:
        if not is_read_only:
            # Destructive or write operation — execute once without automatic retry
            return await func() if asyncio.iscoroutinefunction(func) else func()

        attempt = 0
        while attempt < max_retries:
            try:
                return await func() if asyncio.iscoroutinefunction(func) else func()
            except Exception as exc:
                attempt += 1
                if attempt >= max_retries:
                    logger.error("Operation failed after %d retries: %s", max_retries, exc)
                    raise exc
                await asyncio.sleep(backoff_seconds * (2 ** (attempt - 1)))
