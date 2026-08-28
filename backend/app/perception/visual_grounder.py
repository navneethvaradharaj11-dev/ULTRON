import logging
from typing import List, Optional
from app.perception.perception_models import VisualElement, GroundingTarget, BoundingBox

logger = logging.getLogger("ULTRON.VisualGrounder")


class VisualGrounder:
    """Grounds natural language instructions to visual UI targets."""

    def ground_instruction(
        self,
        instruction: str,
        elements: List[VisualElement]
    ) -> Optional[GroundingTarget]:
        """Find the best matching visual element for a natural language instruction."""
        if not elements:
            logger.warning(f"No visual elements available for grounding instruction: '{instruction}'")
            return None

        instruction_low = instruction.lower()

        best_element: Optional[VisualElement] = None
        best_score: float = 0.0

        for elem in elements:
            score = 0.0
            label_low = elem.label.lower()
            type_low = elem.type.lower()

            # Exact label match
            if label_low and label_low in instruction_low:
                score += 0.85
            elif label_low and any(word in instruction_low for word in label_low.split()):
                score += 0.60

            # Type match
            if type_low in instruction_low:
                score += 0.15


            # Element confidence factor
            score *= elem.confidence

            if score > best_score:
                best_score = score
                best_element = elem

        if best_element is None or best_score < 0.20:
            # Fallback to first interactive element if score is very low
            interactive_elements = [e for e in elements if e.interactive]
            if interactive_elements:
                best_element = interactive_elements[0]
                best_score = 0.50
            else:
                return None

        requires_approval = best_element.sensitive or "delete" in instruction_low or "pay" in instruction_low

        logger.info(
            f"Grounded instruction '{instruction}' to element '{best_element.id}' "
            f"('{best_element.label}') with confidence {best_score:.2f}"
        )

        return GroundingTarget(
            element_id=best_element.id,
            element_type=best_element.type,
            description=best_element.label or best_element.type,
            bounding_box=best_element.bbox,
            confidence=round(best_score, 2),
            requires_approval=requires_approval,
            warning="Low confidence grounding" if best_score < 0.60 else None
        )
