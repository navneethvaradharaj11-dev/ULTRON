import logging
from typing import List, Dict, Any, Optional
from app.perception.perception_models import PerceptionResult, VisualElement, BoundingBox

logger = logging.getLogger("ULTRON.PerceptionFusion")


class PerceptionFusion:
    """Fuses multi-modal perception sources (DOM, Accessibility, OCR, Vision) into a normalized representation."""

    def fuse_perception_sources(
        self,
        dom_elements: Optional[List[Dict[str, Any]]] = None,
        accessibility_elements: Optional[List[VisualElement]] = None,
        ocr_regions: Optional[List[Any]] = None,
        vision_result: Optional[PerceptionResult] = None
    ) -> Dict[str, Any]:
        """Combine multi-modal sources into a unified perception graph."""
        fused_elements: Dict[str, Dict[str, Any]] = {}
        warnings: List[str] = []

        # 1. Base from DOM if available (cheapest reliable source)
        if dom_elements:
            for d in dom_elements:
                elem_id = d.get("id", f"dom_{len(fused_elements)}")
                rect = d.get("rect", {"x": 0, "y": 0, "width": 100, "height": 40})
                fused_elements[elem_id] = {
                    "element_id": elem_id,
                    "label": d.get("text", d.get("label", "")),
                    "type": d.get("tag", "element").lower(),
                    "bbox": rect,
                    "sources": ["dom"],
                    "confidence": 0.95,
                    "interactive": True,
                    "sensitive": d.get("sensitive", False)
                }

        # 2. Layer Accessibility information
        if accessibility_elements:
            for a11y in accessibility_elements:
                found = False
                for elem_id, item in fused_elements.items():
                    if self._boxes_overlap(item["bbox"], a11y.bbox.model_dump()):
                        item["sources"].append("accessibility")
                        item["confidence"] = min(1.0, item["confidence"] + 0.03)
                        found = True
                        break
                if not found:
                    fused_elements[a11y.id] = {
                        "element_id": a11y.id,
                        "label": a11y.label,
                        "type": a11y.type,
                        "bbox": a11y.bbox.model_dump(),
                        "sources": ["accessibility"],
                        "confidence": 0.92,
                        "interactive": a11y.interactive,
                        "sensitive": a11y.sensitive
                    }

        # 3. Layer Vision result
        if vision_result and vision_result.elements:
            for v_elem in vision_result.elements:
                found = False
                for elem_id, item in fused_elements.items():
                    if self._boxes_overlap(item["bbox"], v_elem.bbox.model_dump()):
                        item["sources"].append("vision")
                        item["confidence"] = min(1.0, item["confidence"] + 0.02)
                        found = True
                        break
                if not found:
                    fused_elements[v_elem.id] = {
                        "element_id": v_elem.id,
                        "label": v_elem.label,
                        "type": v_elem.type,
                        "bbox": v_elem.bbox.model_dump(),
                        "sources": ["vision"],
                        "confidence": v_elem.confidence,
                        "interactive": v_elem.interactive,
                        "sensitive": v_elem.sensitive
                    }

        # 4. Layer OCR regions
        if ocr_regions:
            for ocr in ocr_regions:
                txt = getattr(ocr, "text", "")
                box = getattr(ocr, "bbox", None)
                box_dict = box.model_dump() if hasattr(box, "model_dump") else box
                if box_dict:
                    for elem_id, item in fused_elements.items():
                        if self._boxes_overlap(item["bbox"], box_dict):
                            item["sources"].append("ocr")
                            if not item["label"]:
                                item["label"] = txt

        # Check for perception conflict / disagreement
        conflicts = [item for item in fused_elements.values() if item["confidence"] < 0.60]
        if conflicts:
            warnings.append(f"Perception disagreement on {len(conflicts)} elements. Triggering REASSESS.")

        result_list = list(fused_elements.values())
        avg_confidence = (
            sum(item["confidence"] for item in result_list) / len(result_list)
            if result_list else 0.0
        )

        logger.info(f"PerceptionFusion synthesized {len(result_list)} elements (avg confidence: {avg_confidence:.2f})")

        return {
            "elements": result_list,
            "total_count": len(result_list),
            "confidence": round(avg_confidence, 2),
            "warnings": warnings,
            "requires_approval": any(item.get("sensitive") for item in result_list)
        }

    def _boxes_overlap(self, box1: Dict[str, Any], box2: Dict[str, Any]) -> bool:
        b1_x, b1_y, b1_w, b1_h = box1.get("x", 0), box1.get("y", 0), box1.get("width", 0), box1.get("height", 0)
        b2_x, b2_y, b2_w, b2_h = box2.get("x", 0), box2.get("y", 0), box2.get("width", 0), box2.get("height", 0)

        return not (
            b1_x + b1_w < b2_x or
            b2_x + b2_w < b1_x or
            b1_y + b1_h < b2_y or
            b2_y + b2_h < b1_y
        )
