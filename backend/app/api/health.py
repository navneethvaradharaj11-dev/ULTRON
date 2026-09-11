from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.database.connection import get_db
from app.config.settings import settings
from app.tools.registry import default_tool_registry

router = APIRouter(tags=["Health"])


@router.get("/health")
@router.get("/api/v1/health")
@router.get("/api/v1/health/check")
async def health_check(db: AsyncSession = Depends(get_db)):


    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "system": "ULTRON Agentic AI Operating System",
        "version": "12.0.0",
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


@router.get("/health/live")
@router.get("/api/v1/health/live")
async def liveness_check():
    """Liveness probe for container orchestrator."""
    return {"status": "live", "system": "ULTRON Core"}


@router.get("/health/ready")
@router.get("/api/v1/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):

    """Readiness probe checking MySQL, Redis, Sandbox, and Filesystem readiness."""
    components = {}

    # 1. MySQL Check
    try:
        await db.execute(text("SELECT 1"))
        components["database"] = "ready"
    except Exception as e:
        components["database"] = f"failed: {e}"

    # 2. Redis Check
    from app.engine.redis_client import redis_client
    components["redis"] = "ready" if redis_client.is_available else "degraded_in_memory"

    # 3. Sandbox Storage Check
    import os
    sandbox_path = os.path.join(os.getcwd(), "sandbox")
    components["sandbox_storage"] = "ready" if os.path.exists(sandbox_path) or os.access(os.getcwd(), os.W_OK) else "failed"

    all_ready = all(v == "ready" or "degraded" in v for v in components.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "components": components
    }

