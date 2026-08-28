import logging
from typing import Dict, Any, List, Optional
from app.autonomy.trigger import BaseTrigger, TriggerDefinition

logger = logging.getLogger("ULTRON.TriggerRegistry")


class TriggerRegistry:
    """Registry maintaining active trigger registrations."""

    def __init__(self):
        self._triggers: Dict[str, BaseTrigger] = {}

    def register_trigger(self, trigger: BaseTrigger) -> None:
        self._triggers[trigger.definition.trigger_id] = trigger
        logger.info("Registered trigger '%s' (Rule: %s, Type: %s)", trigger.definition.trigger_id, trigger.definition.rule_id, trigger.definition.trigger_type)

    def unregister_trigger(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def get_triggers_for_user(self, user_id: str) -> List[BaseTrigger]:
        return [trig for trig in self._triggers.values() if trig.definition.user_id == user_id]

    def get_all_triggers(self) -> List[BaseTrigger]:
        return list(self._triggers.values())
