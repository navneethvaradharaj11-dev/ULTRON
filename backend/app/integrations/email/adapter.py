import logging
from typing import Dict, Any, Optional
from app.integrations.contracts import IntegrationDescriptor, OperationDescriptor
from app.integrations.integration_registry import integration_registry
from app.integrations.email.client import EmailClient

logger = logging.getLogger("ULTRON.Integrations.EmailAdapter")


class EmailAdapter:
    """Email Service Adapter wrapping email operations with policy metadata."""

    INTEGRATION_ID = "email"

    def __init__(self, client: Optional[EmailClient] = None):
        self.client = client or EmailClient()
        self._register_descriptor()

    def _register_descriptor(self):
        desc = IntegrationDescriptor(
            id=self.INTEGRATION_ID,
            name="Email",
            version="1.0.0",
            provider="Email",
            description="Provider-Neutral Email Integration",
            capabilities=["autonomy", "notifications"],
            risk_level="HIGH",
            authentication_type="OAUTH2",
            required_scopes=["READ_EMAIL", "SEARCH_EMAIL", "CREATE_DRAFT", "SEND_EMAIL", "DELETE_EMAIL"],
            supported_operations={
                "search_messages": OperationDescriptor(
                    operation_id="search_messages",
                    description="Search email messages",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["SEARCH_EMAIL"]
                ),
                "create_draft": OperationDescriptor(
                    operation_id="create_draft",
                    description="Create an email draft",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["CREATE_DRAFT"]
                ),
                "send_message": OperationDescriptor(
                    operation_id="send_message",
                    description="Send an email message to recipient",
                    risk_level="HIGH",
                    requires_approval=True,
                    required_scopes=["SEND_EMAIL"]
                )
            }
        )
        integration_registry.register(desc)

    async def execute(self, operation_id: str, parameters: Dict[str, Any]) -> Any:
        op = operation_id.lower()
        if op == "search_messages":
            return await self.client.search_messages(parameters.get("query", ""))
        elif op == "create_draft":
            return await self.client.create_draft(parameters.get("recipient", "user@ultron.ai"), parameters.get("subject", "Draft"), parameters.get("body", ""))
        elif op == "send_message":
            return await self.client.send_message(parameters.get("recipient", "user@ultron.ai"), parameters.get("subject", "Message"), parameters.get("body", ""))
        else:
            raise ValueError(f"Unsupported Email operation '{op}'")
