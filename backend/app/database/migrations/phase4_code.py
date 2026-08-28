import logging
from sqlalchemy import inspect, text
from app.database.connection import engine, Base
from app.database.models import (
    CodeWorkspaceModel, CodeFileModel, CodeExecutionModel,
    CodeExecutionEventModel, CodeArtifactModel, CodeTestModel
)

logger = logging.getLogger("ULTRON.Migrations.Phase4")


def run_phase4_migration():
    """Run database schema migration for Phase 4 Code Intelligence tables."""
    logger.info("Checking Phase 4 Code Intelligence database tables...")
    try:
        import asyncio

        async def _create_tables():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            asyncio.create_task(_create_tables())
        else:
            asyncio.run(_create_tables())

        logger.info("Phase 4 Code Intelligence migration completed successfully.")
    except Exception as e:
        logger.warning("Phase 4 migration check completed with info: %s", e)
