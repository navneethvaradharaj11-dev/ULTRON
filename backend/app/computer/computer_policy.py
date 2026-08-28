import logging
from typing import Dict, Any, Tuple
from app.config.settings import settings

logger = logging.getLogger("ULTRON.ComputerPolicy")


class ComputerPolicy:
    """Evaluates security risk, approval requirements, coordinate bounds, and confidence thresholds."""

    SENSITIVE_KEYWORDS = [
        "delete", "remove", "pay", "buy", "purchase", "transfer", "submit payment",
        "password", "credit card", "security", "admin", "install", "credential",
        "settings", "checkout", "send message"
    ]

    FORBIDDEN_ACTIONS = [
        "modify_registry", "extract_credentials", "execute_raw_shell", "disable_firewall"
    ]

    def evaluate_action_risk(
        self,
        action_type: str,
        target: Dict[str, Any],
        parameters: Dict[str, Any],
        confidence: float,
        viewport_width: int = 1280,
        viewport_height: int = 800
    ) -> Tuple[str, str]:
        """Returns (approval_state, reason) where approval_state is AUTO_APPROVED, REQUIRES_APPROVAL, or FORBIDDEN."""
        act_lower = action_type.lower()
        if act_lower in self.FORBIDDEN_ACTIONS:
            return "FORBIDDEN", f"Action '{action_type}' is strictly forbidden by Computer Policy."

        # 1. Confidence Check
        if confidence < settings.VISION_LOW_CONFIDENCE_THRESHOLD:
            return "FORBIDDEN", f"Action denied: perception confidence {confidence:.2f} < threshold {settings.VISION_LOW_CONFIDENCE_THRESHOLD}"

        # 2. Viewport Bounds Check
        x = parameters.get("x", target.get("x"))
        y = parameters.get("y", target.get("y"))
        if x is not None and y is not None:
            if not (0 <= int(x) <= viewport_width and 0 <= int(y) <= viewport_height):
                return "FORBIDDEN", f"Coordinates ({x}, {y}) are outside active viewport ({viewport_width}x{viewport_height})."

        # 3. Sensitive Target Detection
        label = target.get("label", "") or target.get("description", "")
        text = parameters.get("text", "")
        combined_text = f"{label} {text}".lower()

        if settings.COMPUTER_APPROVAL_REQUIRED and any(kw in combined_text for kw in self.SENSITIVE_KEYWORDS):
            return "REQUIRES_APPROVAL", f"Action targets high-impact or sensitive operations ('{label}')."


        # 4. Confirmation required for medium confidence (0.60 <= confidence < 0.85)
        if settings.VISION_LOW_CONFIDENCE_THRESHOLD <= confidence < settings.VISION_CONFIDENCE_THRESHOLD:
            return "REQUIRES_APPROVAL", f"Medium perception confidence ({confidence:.2f}) requires user confirmation."

        return "AUTO_APPROVED", "Action satisfies safety policy."
