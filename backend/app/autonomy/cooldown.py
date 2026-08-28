import time
import logging
from typing import Dict, Any

logger = logging.getLogger("ULTRON.AutonomyCooldown")

_LAST_EXECUTIONS: Dict[str, float] = {}


class CooldownManager:
    """Enforces cooldown windows preventing trigger storms and infinite loops."""

    @staticmethod
    def is_in_cooldown(rule_id: str, cooldown_seconds: int = 300) -> bool:
        now = time.time()
        last = _LAST_EXECUTIONS.get(rule_id, 0.0)
        if now - last < cooldown_seconds:
            logger.info("Rule '%s' is in cooldown window (%ds remaining)", rule_id, int(cooldown_seconds - (now - last)))
            return True
        return False

    @staticmethod
    def mark_executed(rule_id: str) -> None:
        _LAST_EXECUTIONS[rule_id] = time.time()
