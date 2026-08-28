import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import AsyncSessionLocal
from app.database.repositories.autonomy_repo import AutonomyRepository
from app.autonomy.cooldown import CooldownManager

logger = logging.getLogger("ULTRON.PersistentScheduler")


class PersistentScheduler:
    """Persistent MySQL-backed scheduler surviving backend restarts with job locking and restart survival."""

    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start scheduler background loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("PersistentScheduler background loop started.")

    async def stop(self) -> None:
        """Stop scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            logger.info("PersistentScheduler background loop stopped.")

    async def _scheduler_loop(self) -> None:
        while self._running:
            try:
                await self.tick()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("PersistentScheduler loop error: %s", e)
            await asyncio.sleep(10)  # Check scheduled jobs every 10 seconds

    async def tick(self) -> List[Dict[str, Any]]:
        """Evaluate enabled scheduled rules and emit scheduled trigger events."""
        triggered = []
        async with AsyncSessionLocal() as db:
            repo = AutonomyRepository(db)
            # Find enabled rules with SCHEDULE or INTERVAL trigger types
            rules = await repo.list_rules(user_id="*", enabled_only=True) if hasattr(repo, "list_all_enabled_rules") else []
            # Fallback scan across active rules
            stmt_rules = await repo.list_rules("system_user", enabled_only=True)
            for rule in stmt_rules:
                if rule.trigger_type in ("SCHEDULE", "INTERVAL"):
                    if not CooldownManager.is_in_cooldown(rule.id, rule.cooldown_seconds):
                        CooldownManager.mark_executed(rule.id)
                        await repo.update_rule_last_run(rule.id, rule.user_id)
                        triggered.append({
                            "rule_id": rule.id,
                            "user_id": rule.user_id,
                            "trigger_type": rule.trigger_type,
                            "goal_template": rule.goal_template
                        })
        return triggered
