import logging
from typing import Dict, Any, List, Optional
from app.perception.screenshot_capture import ScreenshotCapture
from app.perception.vision_analyzer import VisionAnalyzer
from app.perception.ui_detector import UIDetector
from app.perception.visual_grounder import VisualGrounder
from app.perception.ocr_engine import OCREngine
from app.perception.accessibility_tree import AccessibilityTree
from app.perception.perception_fusion import PerceptionFusion
from app.perception.perception_models import PerceptionResult, GroundingTarget

logger = logging.getLogger("ULTRON.PerceptionEngine")


class PerceptionEngine:
    """Orchestrates screen capture, visual component detection, multi-modal fusion, and grounding."""

    def __init__(
        self,
        viewport_width: int = 1280,
        viewport_height: int = 800,
        vision_provider: Optional[str] = None
    ):
        self.screenshot_capture = ScreenshotCapture(viewport_width, viewport_height)
        self.vision_analyzer = VisionAnalyzer(provider=vision_provider)
        self.ui_detector = UIDetector()
        self.visual_grounder = VisualGrounder()
        self.ocr_engine = OCREngine()
        self.accessibility_tree = AccessibilityTree()
        self.perception_fusion = PerceptionFusion()

    async def perceive_state(
        self,
        session_id: str,
        execution_id: str,
        page_instance: Optional[Any] = None,
        dom_elements: Optional[List[Dict[str, Any]]] = None,
        accessibility_nodes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Perform full perception workflow (Capture -> Vision -> OCR -> A11y -> Fusion)."""
        logger.info(f"Starting perception workflow for session '{session_id}' (execution '{execution_id}')")

        # 1. Capture Screenshot
        shot_res = await self.screenshot_capture.capture_viewport(session_id, execution_id, page_instance)

        # 2. Vision Analysis
        vision_res: PerceptionResult = await self.vision_analyzer.analyze_image(
            screenshot_id=shot_res["id"],
            image_bytes=shot_res.get("bytes"),
            image_metadata=shot_res.get("metadata"),
            dom_elements=dom_elements
        )

        # 3. Accessibility Tree parsing
        a11y_elements = (
            self.accessibility_tree.parse_accessibility_nodes(accessibility_nodes)
            if accessibility_nodes else []
        )

        # 4. OCR text extraction
        ocr_regions = self.ocr_engine.extract_text(
            image_bytes=shot_res.get("bytes"),
            elements_with_text=dom_elements
        )
        untrusted_ocr_text = self.ocr_engine.sanitize_and_wrap_ocr_text(ocr_regions)

        # 5. Multi-modal Perception Fusion
        fused_data = self.perception_fusion.fuse_perception_sources(
            dom_elements=dom_elements,
            accessibility_elements=a11y_elements,
            ocr_regions=ocr_regions,
            vision_result=vision_res
        )

        return {
            "screenshot_id": shot_res["id"],
            "viewport": {"width": shot_res["width"], "height": shot_res["height"]},
            "elements": fused_data["elements"],
            "total_elements": fused_data["total_count"],
            "confidence": fused_data["confidence"],
            "ocr_text": untrusted_ocr_text,
            "warnings": fused_data["warnings"],
            "requires_approval": fused_data["requires_approval"],
            "timestamp": shot_res["timestamp"]
        }

    def ground_instruction(
        self,
        instruction: str,
        perception_data: Dict[str, Any]
    ) -> Optional[GroundingTarget]:
        """Ground natural language instruction into visual target."""
        raw_elements = perception_data.get("elements", [])
        detected_elements = self.ui_detector.detect_elements(raw_elements)
        return self.visual_grounder.ground_instruction(instruction, detected_elements)
