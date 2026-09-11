import logging
from typing import Dict, Any

logger = logging.getLogger("ULTRON.Core.DegradationManager")


class DegradationManager:
    """Component degradation tracking & circuit breaker manager.
    Prevents single component failures (e.g., external API down) from crashing ULTRON.
    """

    def __init__(self):
        self._component_status: Dict[str, str] = {
            "github": "OPERATIONAL",
            "calendar": "OPERATIONAL",
            "email": "OPERATIONAL",
            "browser": "OPERATIONAL",
            "sandbox": "OPERATIONAL",
            "vision": "OPERATIONAL",
        }

    def set_component_status(self, component: str, status: str) -> None:
        """Update component operational state (e.g. OPERATIONAL, DEGRADED, FAILED)."""
        old_status = self._component_status.get(component, "UNKNOWN")
        self._component_status[component] = status.upper()
        if old_status != status.upper():
            logger.warning("Component '%s' status changed: %s -> %s", component, old_status, status.upper())

    def get_component_status(self, component: str) -> str:
        """Get status of a specific component."""
        return self._component_status.get(component, "UNKNOWN")

    def is_operational(self, component: str) -> bool:
        """Check if component is operational."""
        return self.get_component_status(component) == "OPERATIONAL"

    def get_all_statuses(self) -> Dict[str, str]:
        """Get snapshot of all component statuses."""
        return self._component_status.copy()


degradation_manager = DegradationManager()
