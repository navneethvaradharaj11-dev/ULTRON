import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.security.authentication import get_current_user
from app.database.models import User
from app.computer.computer_manager import computer_manager
from app.perception.perception_engine import PerceptionEngine

logger = logging.getLogger("ULTRON.PerceptionAPI")
router = APIRouter(prefix="/perception", tags=["Perception Engine"])
engine = PerceptionEngine()


class GroundRequest(BaseModel):
    instruction: str
    perception_data: Dict[str, Any]


class PerceiveRequest(BaseModel):
    execution_id: str
    dom_elements: Optional[List[Dict[str, Any]]] = None


@router.post("/perceive")
async def perceive_state(req: PerceiveRequest, current_user: User = Depends(get_current_user)):
    res = await engine.perceive_state(
        session_id="api_session",
        execution_id=req.execution_id,
        dom_elements=req.dom_elements
    )
    return res


@router.post("/ground")
async def ground_target(req: GroundRequest, current_user: User = Depends(get_current_user)):
    target = engine.ground_instruction(req.instruction, req.perception_data)
    if target:
        return {"status": "success", "target": target.model_dump()}
    return {"status": "failed", "error": "TARGET_NOT_FOUND"}
