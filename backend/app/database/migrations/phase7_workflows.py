import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger(__name__)

PHASE7_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS workflows (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36),
        goal TEXT NOT NULL,
        strategy_id VARCHAR(36),
        current_state VARCHAR(32) NOT NULL DEFAULT 'CREATED',
        progress FLOAT NOT NULL DEFAULT 0.0,
        current_step VARCHAR(64),
        retry_count INT NOT NULL DEFAULT 0,
        replan_count INT NOT NULL DEFAULT 0,
        metadata_json TEXT,
        created_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        started_at DATETIME,
        completed_at DATETIME,
        INDEX idx_workflows_user_id (user_id),
        INDEX idx_workflows_state (current_state)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_steps (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        step_id VARCHAR(64) NOT NULL,
        name VARCHAR(255) NOT NULL,
        assigned_agent VARCHAR(64) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        dependencies_json TEXT,
        input_data_json TEXT,
        output_data_json TEXT,
        error_message TEXT,
        retry_count INT NOT NULL DEFAULT 0,
        duration_ms INT NOT NULL DEFAULT 0,
        started_at DATETIME,
        completed_at DATETIME,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_steps_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_events (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        event_type VARCHAR(64) NOT NULL,
        payload_json TEXT,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_events_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_checkpoints (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        checkpoint_name VARCHAR(128) NOT NULL,
        state_snapshot_json TEXT NOT NULL,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_checkpoints_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_failures (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        task_id VARCHAR(64),
        agent VARCHAR(64),
        failure_type VARCHAR(64) NOT NULL,
        error_message TEXT NOT NULL,
        context_json TEXT,
        recoverable BOOLEAN NOT NULL DEFAULT TRUE,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_failures_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_approvals (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        task_id VARCHAR(64) NOT NULL,
        action_type VARCHAR(64) NOT NULL,
        details_json TEXT,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        decided_by VARCHAR(36),
        decided_at DATETIME,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_approvals_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_results (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        summary TEXT NOT NULL,
        status VARCHAR(32) NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        evidence_json TEXT,
        tasks_completed INT NOT NULL DEFAULT 0,
        tasks_failed INT NOT NULL DEFAULT 0,
        warnings_json TEXT,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_results_workflow_id (workflow_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_artifacts (
        id VARCHAR(36) PRIMARY KEY,
        workflow_id VARCHAR(36) NOT NULL,
        filename VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        artifact_type VARCHAR(64) NOT NULL,
        size_bytes INT NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL,
        FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
        INDEX idx_wf_artifacts_workflow_id (workflow_id)
    );
    """
]

def run_phase7_migrations():
    """Run Phase 7 Autonomous Orchestration & Workflow Engine table migrations."""
    try:
        with engine.connect() as conn:
            for sql_stmt in PHASE7_TABLES_SQL:
                conn.execute(text(sql_stmt))
            conn.commit()
        logger.info("Phase 7 Workflow database migrations executed successfully.")
    except Exception as e:
        logger.warning("Phase 7 Workflow migration note: %s", e)
