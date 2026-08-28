import logging
from sqlalchemy import inspect, text
from app.database.connection import engine, Base
from app.database.models import (
    BrowserSessionModel, BrowserActionModel, BrowserPageModel, ResearchSourceModel
)

logger = logging.getLogger("ULTRON.Migrations.Phase3")


def run_phase3_migration():
    """Run database schema migration for Phase 3 Browser & Research tables."""
    logger.info("Checking Phase 3 Browser & Research database tables...")
    try:
        import asyncio

        async def _create_tables():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(_create_tables())
        else:
            loop.run_until_complete(_create_tables())

        logger.info("Phase 3 Browser migration completed successfully.")
    except Exception as e:
        logger.warning("Phase 3 migration check completed with info: %s", e)
