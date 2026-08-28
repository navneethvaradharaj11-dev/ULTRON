import logging
from typing import List, Optional, Dict, Any
from app.perception.perception_models import TextRegion, BoundingBox

logger = logging.getLogger("ULTRON.OCREngine")


class OCREngine:
    """Extracts visible text from screenshot images and enforces untrusted data block wrapping."""

    def extract_text(
        self,
        image_bytes: Optional[bytes] = None,
        image_metadata: Optional[Dict[str, Any]] = None,
        elements_with_text: Optional[List[Dict[str, Any]]] = None
    ) -> List[TextRegion]:
        """Extract text regions from image or element metadata."""
        regions: List[TextRegion] = []

        if elements_with_text:
            for idx, item in enumerate(elements_with_text):
                text = item.get("text", "").strip()
                if text:
                    rect = item.get("rect", {"x": 10, "y": 10, "width": 100, "height": 30})
                    bbox = BoundingBox(
                        x=int(rect.get("x", 0)),
                        y=int(rect.get("y", 0)),
                        width=int(rect.get("width", 100)),
                        height=int(rect.get("height", 30))
                    )
                    regions.append(
                        TextRegion(
                            id=f"ocr_txt_{idx}",
                            text=text,
                            bbox=bbox,
                            confidence=float(item.get("confidence", 0.95))
                        )
                    )

        logger.info(f"OCREngine extracted {len(regions)} text regions")
        return regions

    def sanitize_and_wrap_ocr_text(self, text_regions: List[TextRegion]) -> str:
        """Wrap extracted OCR text inside UNTRUSTED VISUAL DATA isolation block to prevent prompt injection."""
        joined_text = "\n".join([f"[{r.id}] ({r.bbox.x},{r.bbox.y}): {r.text}" for r in text_regions])
        return (
            "\n--- BEGIN UNTRUSTED OCR VISUAL DATA ---\n"
            f"{joined_text}\n"
            "--- END UNTRUSTED OCR VISUAL DATA ---\n"
        )
