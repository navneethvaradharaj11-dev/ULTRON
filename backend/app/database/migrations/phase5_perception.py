import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger("ULTRON.Migration")

PHASE5_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS computer_sessions (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
        viewport_width INT NOT NULL DEFAULT 1280,
        viewport_height INT NOT NULL DEFAULT 800,
        started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at DATETIME NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_comp_sessions_user_id (user_id),
        INDEX idx_comp_sessions_execution_id (execution_id),
        INDEX idx_comp_sessions_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS computer_screenshots (
        id VARCHAR(36) PRIMARY KEY,
        session_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        image_metadata JSON NULL,
        width INT NOT NULL DEFAULT 1280,
        height INT NOT NULL DEFAULT 800,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES computer_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_comp_screenshots_session_id (session_id),
        INDEX idx_comp_screenshots_execution_id (execution_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS perception_results (
        id VARCHAR(36) PRIMARY KEY,
        screenshot_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        result_json JSON NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 0.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (screenshot_id) REFERENCES computer_screenshots(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_percep_results_screenshot_id (screenshot_id),
        INDEX idx_percep_results_execution_id (execution_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS computer_actions (
        id VARCHAR(36) PRIMARY KEY,
        session_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        action_type VARCHAR(50) NOT NULL,
        target_json JSON NULL,
        parameters_json JSON NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
        approval_state VARCHAR(50) NOT NULL DEFAULT 'AUTO_APPROVED',
        confidence FLOAT NOT NULL DEFAULT 1.0,
        result_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME NULL,
        FOREIGN KEY (session_id) REFERENCES computer_sessions(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_comp_actions_session_id (session_id),
        INDEX idx_comp_actions_execution_id (execution_id),
        INDEX idx_comp_actions_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]


async def run_phase5_migrations():
    """Execute Phase 5 DDL statements to ensure tables exist in MySQL."""
    try:
        async with engine.begin() as conn:
            for sql in PHASE5_TABLES_SQL:
                await conn.execute(text(sql.strip()))
        logger.info("Phase 5 computer interaction and perception database migration completed successfully.")
    except Exception as e:
        logger.warning(f"Phase 5 migration check notice: {e}")
