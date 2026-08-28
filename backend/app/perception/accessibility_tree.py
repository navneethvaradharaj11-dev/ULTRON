import logging
from typing import List, Dict, Any, Optional
from app.perception.perception_models import VisualElement, BoundingBox

logger = logging.getLogger("ULTRON.AccessibilityTree")


class AccessibilityTree:
    """Retrieves accessibility information and combines it with visual perception."""

    def parse_accessibility_nodes(self, raw_tree: List[Dict[str, Any]]) -> List[VisualElement]:
        nodes: List[VisualElement] = []

        for idx, node in enumerate(raw_tree):
            role = node.get("role", "button").lower()
            name = node.get("name", node.get("value", ""))
            rect = node.get("bounds", {"x": 0, "y": 0, "width": 100, "height": 40})

            bbox = BoundingBox(
                x=int(rect.get("x", 0)),
                y=int(rect.get("y", 0)),
                width=int(rect.get("width", 100)),
                height=int(rect.get("height", 40))
            )

            nodes.append(
                VisualElement(
                    id=node.get("id", f"a11y_node_{idx}"),
                    type=self._map_role(role),
                    label=name,
                    bbox=bbox,
                    confidence=0.98,
                    interactive=node.get("disabled", False) is False,
                    attributes=node
                )
            )

        logger.info(f"AccessibilityTree parsed {len(nodes)} accessibility nodes")
        return nodes

    def _map_role(self, role: str) -> str:
        if "button" in role:
            return "button"
        if "textbox" in role or "input" in role:
            return "text_field"
        if "checkbox" in role:
            return "checkbox"
        if "link" in role:
            return "link"
        if "tab" in role:
            return "tab"
        if "dialog" in role:
            return "dialog"
        return "element"
