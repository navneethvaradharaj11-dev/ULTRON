import logging
from typing import Dict, Any, List

logger = logging.getLogger("ULTRON.Integrations.HealthManager")


class HealthManager:
    """Tracks real-time health status per integration (CONNECTED, DISCONNECTED, AUTH_REQUIRED, RATE_LIMITED, DEGRADED)."""

    def __init__(self):
        self._statuses: Dict[str, str] = {}

    def set_status(self, integration_id: str, status: str) -> None:
        self._statuses[integration_id.lower()] = status
        logger.info("Updated integration '%s' health status to '%s'", integration_id, status)

    def get_status(self, integration_id: str) -> str:
        return self._statuses.get(integration_id.lower(), "CONNECTED")

    def get_all_statuses(self) -> Dict[str, str]:
        return dict(self._statuses)


# Global singleton instance
health_manager = HealthManager()
