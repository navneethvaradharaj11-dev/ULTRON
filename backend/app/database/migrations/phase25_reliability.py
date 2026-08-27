"""
Phase 2.5 Migration — Agentic Reliability & Evaluation
Adds:
  - idempotency_key column to executions table (prevents duplicate executions)
  - execution_metrics table (per-agent performance tracking)
"""
import logging
from sqlalchemy import create_engine, text
from app.config.settings import settings

logger = logging.getLogger("ULTRON.Migration.Phase25")


def run_phase25_migration():
    """Apply Phase 2.5 schema changes to MySQL database."""
    engine = create_engine(settings.database_url_sync, echo=False)

    with engine.begin() as conn:
        # ----------------------------------------------------------------
        # 1. Add idempotency_key to executions (nullable, unique)
        # ----------------------------------------------------------------
        try:
            conn.execute(text(
                "ALTER TABLE executions "
                "ADD COLUMN idempotency_key VARCHAR(128) UNIQUE NULL "
                "COMMENT 'Client-supplied key to prevent duplicate executions';"
            ))
            logger.info("Phase 2.5: Added idempotency_key to executions.")
        except Exception as e:
            if "Duplicate column" in str(e) or "1060" in str(e):
                logger.info("Phase 2.5: idempotency_key already exists — skipping.")
            else:
                logger.warning("Phase 2.5 idempotency_key warning: %s", e)

        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_executions_idempotency_key "
                "ON executions(idempotency_key);"
            ))
        except Exception:
            pass  # Index may already exist

        # ----------------------------------------------------------------
        # 2. Create execution_metrics table
        # ----------------------------------------------------------------
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS execution_metrics (
                    id              VARCHAR(36)  NOT NULL PRIMARY KEY,
                    execution_id    VARCHAR(36)  NOT NULL,
                    task_id         VARCHAR(36)  NULL,
                    agent_name      VARCHAR(50)  NOT NULL,
                    duration_ms     INT          NOT NULL DEFAULT 0,
                    status          VARCHAR(50)  NOT NULL,
                    retry_count     INT          NOT NULL DEFAULT 0,
                    tools_used_json JSON         NULL,
                    review_status   VARCHAR(50)  NULL,
                    review_confidence INT        NOT NULL DEFAULT 0,
                    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_em_execution FOREIGN KEY (execution_id)
                        REFERENCES executions(id) ON DELETE CASCADE,
                    CONSTRAINT fk_em_task FOREIGN KEY (task_id)
                        REFERENCES execution_tasks(id) ON DELETE CASCADE,
                    INDEX idx_em_execution_id (execution_id),
                    INDEX idx_em_agent_name (agent_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """))
            logger.info("Phase 2.5: Created execution_metrics table.")
        except Exception as e:
            if "already exists" in str(e) or "1050" in str(e):
                logger.info("Phase 2.5: execution_metrics already exists — skipping.")
            else:
                logger.warning("Phase 2.5 execution_metrics warning: %s", e)

    logger.info("Phase 2.5 migration complete.")


if __name__ == "__main__":
    run_phase25_migration()
