import logging
from typing import List, Dict, Any
from app.perception.perception_models import VisualElement, BoundingBox

logger = logging.getLogger("ULTRON.UIDetector")


class UIDetector:
    """Detects and classifies UI components (buttons, text fields, checkboxes, dropdowns, dialogs, etc.)."""

    SUPPORTED_TYPES = [
        "button", "text_field", "checkbox", "radio_button", "dropdown",
        "link", "tab", "menu", "dialog", "table", "card", "icon", "nav_element"
    ]

    def detect_elements(self, raw_features: List[Dict[str, Any]]) -> List[VisualElement]:
        detected: List[VisualElement] = []

        for idx, feat in enumerate(raw_features):
            element_id = feat.get("id") or feat.get("element_id") or f"ui_elem_{idx}"
            raw_type = (feat.get("type") or feat.get("tag") or "button").lower()


            norm_type = self._normalize_type(raw_type)
            label = feat.get("label", feat.get("text", ""))

            rect = feat.get("bbox", {"x": 0, "y": 0, "width": 100, "height": 40})
            if isinstance(rect, dict):
                bbox = BoundingBox(
                    x=int(rect.get("x", 0)),
                    y=int(rect.get("y", 0)),
                    width=int(rect.get("width", 100)),
                    height=int(rect.get("height", 40))
                )
            else:
                bbox = rect

            confidence = float(feat.get("confidence", 0.90))
            interactive = feat.get("interactive", True)
            sensitive = feat.get("sensitive", self._is_sensitive_label(label, norm_type))

            element = VisualElement(
                id=element_id,
                type=norm_type,
                label=label,
                bbox=bbox,
                confidence=confidence,
                interactive=interactive,
                sensitive=sensitive,
                attributes=feat.get("attributes", {})
            )
            detected.append(element)

        logger.info(f"UIDetector identified {len(detected)} UI components")
        return detected

    def _normalize_type(self, raw_type: str) -> str:
        if "btn" in raw_type or "button" in raw_type or "submit" in raw_type:
            return "button"
        if "input" in raw_type or "text" in raw_type or "field" in raw_type:
            return "text_field"
        if "check" in raw_type:
            return "checkbox"
        if "radio" in raw_type:
            return "radio_button"
        if "select" in raw_type or "drop" in raw_type or "menu" in raw_type:
            return "dropdown"
        if "link" in raw_type or "url" in raw_type or "a" == raw_type:
            return "link"
        if "tab" in raw_type:
            return "tab"
        if "dialog" in raw_type or "modal" in raw_type or "popup" in raw_type:
            return "dialog"
        if "table" in raw_type or "grid" in raw_type:
            return "table"
        if "card" in raw_type:
            return "card"
        if "icon" in raw_type:
            return "icon"
        return "nav_element"

    def _is_sensitive_label(self, label: str, norm_type: str) -> bool:
        low = label.lower()
        sensitive_keywords = [
            "delete", "remove", "pay", "buy", "purchase", "transfer", "submit payment",
            "password", "credit card", "security", "admin", "install"
        ]
        return any(kw in low for kw in sensitive_keywords)
