from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.registry import default_tool_registry
from app.database.connection import get_db
from app.security.authentication import get_current_user
from app.database.models import User

router = APIRouter(prefix="/api/v1/tools", tags=["Tools"])


class ToolExecuteRequest(BaseModel):
    tool_name: str
    params: Dict[str, Any]


@router.get("/")
async def list_tools():
    """List all tools registered in ULTRON ToolRegistry."""
    return default_tool_registry.list_tools()


@router.post("/execute")
async def execute_tool(
    req: ToolExecuteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a registered tool safely."""
    res = await default_tool_registry.execute_tool(
        name=req.tool_name,
        params=req.params,
        user_id=current_user.id,
        db=db
    )
    return res
