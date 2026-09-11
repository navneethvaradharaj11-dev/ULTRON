import pytest
from app.integrations.webhook_manager import WebhookManager
from app.integrations.event_mapper import EventMapper


def test_webhook_signature_verification():
    secret = "webhook_secret_key_123"
    payload = b'{"action":"created","issue":{"number":101}}'
    import hmac, hashlib
    valid_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    assert WebhookManager.verify_signature(payload, valid_sig, secret) is True
    assert WebhookManager.verify_signature(payload, "invalid_sig", secret) is False


def test_event_mapper():
    event = EventMapper.map_to_autonomy_event("github", "issue.created", "user_101", {"issue_id": 101})
    assert event.event_type == "github.issue.created"
    assert event.source == "github"
