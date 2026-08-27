from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database.connection import get_db
from app.config.settings import settings
from app.tools.registry import default_tool_registry

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "system": "ULTRON Core AI OS",
        "version": "1.0.0-phase1",
        "database": {
            "engine": "mysql",
            "status": db_status
        },
        "ai_provider": {
            "name": settings.AI_PROVIDER,
            "model": settings.AI_MODEL_NAME
        },
        "registered_tools_count": len(default_tool_registry.list_tools())
    }
