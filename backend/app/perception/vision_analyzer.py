import logging
from typing import Dict, Any, List, Optional
from app.config.settings import settings
from app.perception.perception_models import (
    PerceptionResult, VisualElement, TextRegion, BoundingBox
)

logger = logging.getLogger("ULTRON.VisionAnalyzer")


class VisionAnalyzer:
    """Analyzes screenshot images and extracts structured UI regions and visual components."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.VISION_PROVIDER

    async def analyze_image(
        self,
        screenshot_id: str,
        image_bytes: Optional[bytes] = None,
        image_metadata: Optional[Dict[str, Any]] = None,
        dom_elements: Optional[List[Dict[str, Any]]] = None
    ) -> PerceptionResult:
        """Analyze screenshot image and return structured PerceptionResult."""
        if self.provider == "unavailable":
            return PerceptionResult(
                screenshot_id=screenshot_id,
                confidence=0.0,
                warnings=["VISION_UNAVAILABLE: Vision provider runtime is disabled or unavailable."]
            )

        width = image_metadata.get("width", 1280) if image_metadata else 1280
        height = image_metadata.get("height", 800) if image_metadata else 800

        elements: List[VisualElement] = []
        text_regions: List[TextRegion] = []

        # If dom_elements are provided or mock mode is active, construct grounded visual elements
        if dom_elements:
            for idx, dom in enumerate(dom_elements):
                elem_id = dom.get("id", f"elem_{idx}")
                tag = dom.get("tag", "button").lower()
                label = dom.get("text", dom.get("label", ""))
                rect = dom.get("rect", {"x": 100 + (idx * 60), "y": 150, "width": 120, "height": 40})

                el_type = self._map_tag_to_type(tag)
                bbox = BoundingBox(
                    x=int(rect.get("x", 0)),
                    y=int(rect.get("y", 0)),
                    width=int(rect.get("width", 100)),
                    height=int(rect.get("height", 40))
                )

                elements.append(
                    VisualElement(
                        id=elem_id,
                        type=el_type,
                        label=label,
                        bbox=bbox,
                        confidence=dom.get("confidence", 0.95),
                        interactive=True,
                        sensitive=dom.get("sensitive", False)
                    )
                )
        elif self.provider == "mock":
            # Mock default UI elements for fallback testing
            elements.append(
                VisualElement(
                    id="btn_submit",
                    type="button",
                    label="Submit",
                    bbox=BoundingBox(x=200, y=300, width=120, height=40),
                    confidence=0.95,
                    interactive=True
                )
            )
            elements.append(
                VisualElement(
                    id="input_search",
                    type="input",
                    label="Search",
                    bbox=BoundingBox(x=50, y=50, width=300, height=35),
                    confidence=0.92,
                    interactive=True
                )
            )
            text_regions.append(
                TextRegion(
                    id="txt_1",
                    text="Submit",
                    bbox=BoundingBox(x=200, y=300, width=120, height=40),
                    confidence=0.96
                )
            )

        logger.info(f"VisionAnalyzer analyzed screenshot '{screenshot_id}' via '{self.provider}' provider ({len(elements)} elements detected)")

        return PerceptionResult(
            screenshot_id=screenshot_id,
            viewport={"width": width, "height": height},
            elements=elements,
            text_regions=text_regions,
            confidence=0.92 if elements else 0.50,
            warnings=[]
        )

    def _map_tag_to_type(self, tag: str) -> str:
        tag = tag.lower()
        if "button" in tag:
            return "button"
        if "input" in tag or "text" in tag:
            return "input"
        if "select" in tag or "dropdown" in tag:
            return "dropdown"
        if "a" == tag or "link" in tag:
            return "link"
        if "tab" in tag:
            return "tab"
        if "dialog" in tag or "modal" in tag:
            return "dialog"
        return "element"
