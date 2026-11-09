import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.integrations.email.models import EmailMessageModel

logger = logging.getLogger("ULTRON.Integrations.EmailClient")


class EmailClient:
    """Mock/Real provider-neutral email client."""

    async def search_messages(self, query: str) -> List[Dict[str, Any]]:
        msg = EmailMessageModel(
            id="msg_101",
            subject="ULTRON Phase 11 Report",
            sender="lead@ultron.ai",
            recipient="user@ultron.ai",
            body="Phase 11 integration tests are completed.",
            date=datetime.utcnow().isoformat()
        )
        return [msg.model_dump() if hasattr(msg, "model_dump") else msg.dict()]

    async def create_draft(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        msg = EmailMessageModel(
            id="draft_1",
            subject=subject,
            sender="user@ultron.ai",
            recipient=recipient,
            body=body,
            date=datetime.utcnow().isoformat(),
            is_draft=True
        )
        return msg.model_dump() if hasattr(msg, "model_dump") else msg.dict()

    async def send_message(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        return {"sent": True, "recipient": recipient, "subject": subject, "timestamp": datetime.utcnow().isoformat()}
