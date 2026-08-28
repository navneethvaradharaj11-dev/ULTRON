import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.autonomy.contracts import TriggerType

logger = logging.getLogger("ULTRON.Trigger")


class TriggerDefinition(BaseModel):
    trigger_id: str
    rule_id: str
    user_id: str
    trigger_type: TriggerType
    source: str
    config: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    last_triggered_at: Optional[str] = None
    next_run_at: Optional[str] = None


class BaseTrigger:
    """Base Trigger representation. Triggers DO NOT execute workflows directly; they produce events."""

    def __init__(self, definition: TriggerDefinition):
        self.definition = definition

    def should_trigger(self, event_data: Optional[Dict[str, Any]] = None) -> bool:
        if not self.definition.enabled:
            return False
        return True

    def create_event_payload(self, raw_content: str = "") -> Dict[str, Any]:
        return {
            "trigger_id": self.definition.trigger_id,
            "rule_id": self.definition.rule_id,
            "user_id": self.definition.user_id,
            "trigger_type": self.definition.trigger_type.value,
            "source": self.definition.source,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_content": raw_content
        }
