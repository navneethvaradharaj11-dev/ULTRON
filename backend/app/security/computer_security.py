import logging
from typing import Dict, Any, Tuple, Optional
from app.config.settings import settings
from app.computer.computer_session import ComputerSession

logger = logging.getLogger("ULTRON.ComputerSecurity")


class ComputerSecurityValidator:
    """Security guard enforcing ownership, bounds, rate limits, sensitive targets, confidence, and prompt injection defense."""

    def validate_session_access(self, session: Optional[ComputerSession], requested_user_id: str) -> Tuple[bool, str]:
        """Validate session existence and tenant ownership."""
        if session is None:
            return False, "COMPUTER_UNAVAILABLE: Active session not found or expired."

        if not session.is_active():
            return False, "SESSION_EXPIRED: Computer interaction session is closed."

        if session.user_id != requested_user_id:
            return False, "ACCESS_DENIED: Cross-user session access prohibited."

        return True, "Authorized"

    def validate_action_safety(
        self,
        session: ComputerSession,
        action_type: str,
        target: Dict[str, Any],
        parameters: Dict[str, Any],
        confidence: float
    ) -> Tuple[bool, str, str]:
        """Returns (is_allowed, approval_state, reason)."""
        # 1. Action Limit Enforcement
        if session.action_count >= settings.MAX_COMPUTER_ACTIONS:
            return False, "FORBIDDEN", f"Exceeded maximum action limit ({settings.MAX_COMPUTER_ACTIONS})"

        # 2. Confidence Thresholding
        if confidence < settings.VISION_LOW_CONFIDENCE_THRESHOLD:
            return False, "FORBIDDEN", f"LOW_CONFIDENCE: Perception confidence {confidence:.2f} < threshold {settings.VISION_LOW_CONFIDENCE_THRESHOLD}"

        # 3. Viewport Coordinate Bounds Validation
        x = parameters.get("x", target.get("x"))
        y = parameters.get("y", target.get("y"))
        if x is not None and y is not None:
            try:
                x_val, y_val = int(x), int(y)
                if not session.is_within_bounds(x_val, y_val):
                    return False, "FORBIDDEN", f"Coordinates ({x_val}, {y_val}) outside active viewport bounds ({session.viewport_width}x{session.viewport_height})"
            except ValueError:
                return False, "FORBIDDEN", "Invalid coordinate format"

        # 4. Sensitive Target & Approval Check
        label = str(target.get("label", "") or target.get("description", "")).lower()
        text = str(parameters.get("text", "")).lower()
        combined = f"{label} {text}"

        sensitive_keywords = [
            "delete", "remove", "pay", "buy", "purchase", "transfer", "submit payment",
            "password", "credit card", "security", "admin", "install", "credential",
            "send message", "settings"
        ]

        if settings.COMPUTER_APPROVAL_REQUIRED:
            if any(kw in combined for kw in sensitive_keywords):
                return True, "REQUIRES_APPROVAL", f"High-impact sensitive action detected on target '{label}'"

            if settings.VISION_LOW_CONFIDENCE_THRESHOLD <= confidence < settings.VISION_CONFIDENCE_THRESHOLD:
                return True, "REQUIRES_APPROVAL", f"Medium perception confidence ({confidence:.2f}) requires approval"


        return True, "AUTO_APPROVED", "Action validated cleanly"

    def wrap_untrusted_visual_data(self, visual_summary: str) -> str:
        """Wrap OCR or screenshot text data inside UNTRUSTED VISUAL DATA block to block prompt injection attacks."""
        return (
            "\n--- BEGIN UNTRUSTED VISUAL DATA ---\n"
            f"{visual_summary}\n"
            "--- END UNTRUSTED VISUAL DATA ---\n"
        )
