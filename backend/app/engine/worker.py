import time
import signal
import sys
import logging
import asyncio
from typing import Dict, Any
from app.engine.redis_client import redis_client

logger = logging.getLogger("ULTRON.Worker")


class BackgroundWorker:
    """Production Background Worker process for asynchronous workflow execution,
    knowledge ingestion, notifications, and scheduled triggers with graceful shutdown.
    """

    def __init__(self, queue_name: str = "default"):
        self.queue_name = queue_name
        self.running = True
        self._setup_signals()

    def _setup_signals(self):
        try:
            signal.signal(signal.SIGINT, self._handle_shutdown)
            signal.signal(signal.SIGTERM, self._handle_shutdown)
        except (ValueError, AttributeError):
            # Signals might not work on non-main threads or Windows sub-processes
            pass

    def _handle_shutdown(self, signum, frame):
        logger.info("Shutdown signal received (signum=%s). Completing current job before stopping...", signum)
        self.running = False

    async def process_job(self, job: Dict[str, Any]) -> bool:
        """Process a dequeued background task with retry logic and dead-letter handling."""
        job_id = job.get("id", "unknown")
        job_type = job.get("type", "generic")
        retries = job.get("retries", 0)
        max_retries = job.get("max_retries", 3)

        logger.info("Processing job '%s' (type=%s, retry=%s/%s)", job_id, job_type, retries, max_retries)
        try:
            # Simulate job task handling (e.g. knowledge processing, notification delivery)
            await asyncio.sleep(0.1)
            logger.info("Job '%s' completed successfully.", job_id)
            return True
        except Exception as e:
            logger.error("Job '%s' failed with error: %s", job_id, e)
            if retries < max_retries:
                job["retries"] = retries + 1
                logger.info("Re-queuing job '%s' for retry...", job_id)
                redis_client.enqueue_job(self.queue_name, job)
            else:
                logger.error("Job '%s' exceeded max retries (%s). Sending to Dead-Letter Queue (DLQ).", job_id, max_retries)
                redis_client.enqueue_job("dlq", job)
            return False

    async def run(self):
        """Worker main event loop."""
        logger.info("ULTRON Worker started polling queue '%s'...", self.queue_name)
        while self.running:
            try:
                job = redis_client.dequeue_job(self.queue_name)
                if job:
                    await self.process_job(job)
                else:
                    await asyncio.sleep(1.0)
            except Exception as e:
                logger.error("Worker loop exception: %s", e)
                await asyncio.sleep(2.0)
        logger.info("ULTRON Worker shut down gracefully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = BackgroundWorker()
    asyncio.run(worker.run())
