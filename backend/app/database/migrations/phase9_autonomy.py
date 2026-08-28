import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger(__name__)

PHASE9_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS autonomy_rules (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        enabled TINYINT(1) NOT NULL DEFAULT 1,
        trigger_type VARCHAR(64) NOT NULL,
        trigger_config_json JSON NULL,
        goal_template TEXT NOT NULL,
        priority VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
        autonomy_level VARCHAR(32) NOT NULL DEFAULT 'LEVEL_1',
        cooldown_seconds INT NOT NULL DEFAULT 300,
        max_runs_per_hour INT NOT NULL DEFAULT 10,
        last_run_at DATETIME NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_auto_rules_user (user_id),
        INDEX idx_auto_rules_enabled (enabled)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_triggers (
        id VARCHAR(36) PRIMARY KEY,
        rule_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        trigger_type VARCHAR(64) NOT NULL,
        source VARCHAR(255) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
        last_triggered_at DATETIME NULL,
        next_run_at DATETIME NULL,
        config_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_auto_trig_rule (rule_id),
        INDEX idx_auto_trig_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_events (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        rule_id VARCHAR(36) NULL,
        event_type VARCHAR(64) NOT NULL,
        source VARCHAR(255) NOT NULL,
        payload_json JSON NULL,
        importance VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
        deduplication_key VARCHAR(128) NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_auto_evt_user (user_id),
        INDEX idx_auto_evt_dedup (deduplication_key)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_decisions (
        id VARCHAR(36) PRIMARY KEY,
        event_id VARCHAR(36) NOT NULL,
        user_id VARCHAR(36) NOT NULL,
        rule_id VARCHAR(36) NULL,
        decision_type VARCHAR(64) NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        priority VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
        reasoning TEXT NOT NULL,
        evidence_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_auto_dec_event (event_id),
        INDEX idx_auto_dec_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_executions (
        id VARCHAR(36) PRIMARY KEY,
        rule_id VARCHAR(36) NOT NULL,
        workflow_id VARCHAR(36) NULL,
        user_id VARCHAR(36) NOT NULL,
        status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
        result_summary TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME NULL,
        INDEX idx_auto_exec_rule (rule_id),
        INDEX idx_auto_exec_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_notifications (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        rule_id VARCHAR(36) NULL,
        title VARCHAR(255) NOT NULL,
        summary TEXT NOT NULL,
        priority VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
        is_read TINYINT(1) NOT NULL DEFAULT 0,
        payload_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_auto_notif_user (user_id),
        INDEX idx_auto_notif_read (is_read)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_monitor_states (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        target_url_or_path VARCHAR(2048) NOT NULL,
        last_hash VARCHAR(64) NOT NULL,
        last_checked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        change_detected TINYINT(1) NOT NULL DEFAULT 0,
        metadata_json JSON NULL,
        INDEX idx_auto_mon_user (user_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS autonomy_policy_overrides (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        rule_id VARCHAR(36) NOT NULL,
        override_level VARCHAR(32) NOT NULL,
        reason TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_auto_pol_user (user_id)
    );
    """
]


def run_phase9_migrations():
    """Execute DDL migrations for Phase 9 Proactive Autonomous Agent."""
    logger.info("Executing Phase 9 Proactive Autonomous Agent DDL migrations...")
    try:
        with engine.connect() as conn:
            for sql_stmt in PHASE9_TABLES_SQL:
                try:
                    conn.execute(text(sql_stmt))
                    conn.commit()
                except Exception as e:
                    logger.warning("Phase 9 Migration stmt notice: %s", e)
    except Exception as e:
        logger.warning("Phase 9 Migration notice: %s", e)
