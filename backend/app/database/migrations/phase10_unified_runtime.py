import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger(__name__)

PHASE10_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS ultron_commands (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workflow_id VARCHAR(36) NULL,
        raw_message TEXT NOT NULL,
        intent_type VARCHAR(64) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'RECEIVED',
        result_summary TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME NULL,
        INDEX idx_u_cmd_user (user_id),
        INDEX idx_u_cmd_wf (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ultron_capabilities (
        id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(64) UNIQUE NOT NULL,
        description TEXT NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'AVAILABLE',
        risk_level VARCHAR(32) NOT NULL DEFAULT 'LOW',
        requires_approval TINYINT(1) NOT NULL DEFAULT 0,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ultron_project_contexts (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        workspace_id VARCHAR(36) NULL,
        metadata_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_u_proj_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ultron_resource_budgets (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workflow_id VARCHAR(36) NOT NULL,
        max_tool_calls INT NOT NULL DEFAULT 50,
        used_tool_calls INT NOT NULL DEFAULT 0,
        max_runtime_seconds INT NOT NULL DEFAULT 600,
        used_runtime_seconds INT NOT NULL DEFAULT 0,
        max_browser_steps INT NOT NULL DEFAULT 20,
        used_browser_steps INT NOT NULL DEFAULT 0,
        status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
        INDEX idx_u_bud_wf (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS ultron_activity_timeline (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workflow_id VARCHAR(36) NULL,
        activity_type VARCHAR(64) NOT NULL,
        title VARCHAR(255) NOT NULL,
        details TEXT NULL,
        payload_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_u_act_user (user_id),
        INDEX idx_u_act_wf (workflow_id)
    );
    """
]


async def run_phase10_migrations():
    """Execute DDL migrations for Phase 10 Unified Personal Agent Operating System."""
    logger.info("Executing Phase 10 Unified Personal Agent Operating System DDL migrations...")
    try:
        async with engine.begin() as conn:
            for sql_stmt in PHASE10_TABLES_SQL:
                try:
                    await conn.execute(text(sql_stmt))
                except Exception as e:
                    logger.warning("Phase 10 Migration stmt notice: %s", e)
    except Exception as e:
        logger.warning("Phase 10 Migration notice: %s", e)
