import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ULTRON.ElementFinder")


class ElementFinder:
    """Identifies and resolves target elements in a structured page representation using semantic roles, visible text, and attributes."""

    @classmethod
    def find_element(
        cls,
        elements: List[Dict[str, Any]],
        query: str,
        element_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Match query against elements array using text, role, label, id, and type."""
        if not elements or not query:
            return None

        q_lower = query.strip().lower()

        # 1. Exact match on ID
        for elem in elements:
            if str(elem.get("id", "")).lower() == q_lower:
                return elem

        # 2. Exact match on visible text or aria-label
        for elem in elements:
            text = str(elem.get("text", "")).strip().lower()
            label = str(elem.get("label", "")).strip().lower()
            if text == q_lower or label == q_lower:
                if not element_type or str(elem.get("type", "")).lower() == element_type.lower():
                    return elem

        # 3. Substring match on text or label
        for elem in elements:
            text = str(elem.get("text", "")).strip().lower()
            label = str(elem.get("label", "")).strip().lower()
            name = str(elem.get("name", "")).strip().lower()
            placeholder = str(elem.get("placeholder", "")).strip().lower()

            if q_lower in text or q_lower in label or q_lower in name or q_lower in placeholder:
                if not element_type or str(elem.get("type", "")).lower() == element_type.lower():
                    return elem

        # 4. Fallback search by element role or type
        if element_type:
            et_lower = element_type.lower()
            for elem in elements:
                t = str(elem.get("type", "")).lower()
                r = str(elem.get("role", "")).lower()
                if t == et_lower or r == et_lower:
                    return elem

        return None
