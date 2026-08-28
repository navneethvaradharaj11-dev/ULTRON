import logging
from typing import Tuple, Dict, Any, Optional
from app.autonomy.contracts import AutonomyLevel, DecisionType

logger = logging.getLogger("ULTRON.AutonomyPolicy")


class AutonomyPolicyEngine:
    """Evaluates autonomy level policies and enforces risk boundaries."""

    @staticmethod
    def evaluate_policy(
        autonomy_level: AutonomyLevel,
        action_type: str,
        is_sensitive: bool = False
    ) -> Tuple[DecisionType, str]:
        """Evaluate action risk against assigned autonomy level."""

        if autonomy_level == AutonomyLevel.LEVEL_4:
            return DecisionType.DENY, "Autonomy Level 4 FORBIDDEN: Operation is strictly prohibited."

        if is_sensitive or autonomy_level == AutonomyLevel.LEVEL_3:
            return DecisionType.REQUIRE_APPROVAL, "Autonomy Level 3: Sensitive operation requires human approval."

        if autonomy_level == AutonomyLevel.LEVEL_0:
            return DecisionType.IGNORE, "Autonomy Level 0 OBSERVE_ONLY: Observing change without action."

        if autonomy_level == AutonomyLevel.LEVEL_1:
            return DecisionType.NOTIFY, "Autonomy Level 1 NOTIFY_ONLY: Notifying user of event."

        if autonomy_level == AutonomyLevel.LEVEL_2:
            return DecisionType.START_WORKFLOW, "Autonomy Level 2: Low-risk autonomous workflow execution allowed."

        return DecisionType.NOTIFY, "Default autonomy policy evaluation."
