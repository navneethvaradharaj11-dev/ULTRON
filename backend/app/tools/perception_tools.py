import logging
from typing import Dict, Any, Optional, List
from app.perception.perception_engine import PerceptionEngine

logger = logging.getLogger("ULTRON.PerceptionTools")
engine = PerceptionEngine()


async def perception_perceive_state(
    session_id: str,
    execution_id: str,
    dom_elements: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    res = await engine.perceive_state(session_id, execution_id, dom_elements=dom_elements)
    return res


async def perception_ground_target(
    instruction: str,
    perception_data: Dict[str, Any]
) -> Dict[str, Any]:
    grounded = engine.ground_instruction(instruction, perception_data)
    if grounded:
        return {"status": "success", "target": grounded.model_dump()}
    return {"status": "failed", "error": "TARGET_NOT_FOUND: Could not ground instruction to visual element."}
