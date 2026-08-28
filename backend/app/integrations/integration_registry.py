import logging
from typing import Dict, Any, List, Optional
from app.integrations.contracts import IntegrationDescriptor, OperationDescriptor

logger = logging.getLogger("ULTRON.Integrations.Registry")


class IntegrationRegistry:
    """Registry maintaining dynamically registered service integrations and their operation metadata."""

    def __init__(self):
        self._integrations: Dict[str, IntegrationDescriptor] = {}

    def register(self, descriptor: IntegrationDescriptor) -> None:
        """Register a new integration descriptor."""
        self._integrations[descriptor.id.lower()] = descriptor
        logger.info("Registered integration '%s' (v%s)", descriptor.id, descriptor.version)

    def unregister(self, integration_id: str) -> None:
        """Unregister an integration descriptor."""
        key = integration_id.lower()
        if key in self._integrations:
            del self._integrations[key]
            logger.info("Unregistered integration '%s'", integration_id)

    def get(self, integration_id: str) -> Optional[IntegrationDescriptor]:
        """Get integration descriptor by ID."""
        return self._integrations.get(integration_id.lower())

    def list_all(self) -> List[IntegrationDescriptor]:
        """List all registered integration descriptors."""
        return list(self._integrations.values())

    def has(self, integration_id: str) -> bool:
        """Check if integration is registered."""
        return integration_id.lower() in self._integrations

    def health(self, integration_id: str) -> str:
        """Get health status of a specific integration."""
        desc = self.get(integration_id)
        return desc.health_status if desc else "DISCONNECTED"

    def capabilities(self, integration_id: str) -> List[str]:
        """Get capability list for a specific integration."""

        desc = self.get(integration_id)
        return desc.capabilities if desc else []


# Global singleton instance
integration_registry = IntegrationRegistry()
