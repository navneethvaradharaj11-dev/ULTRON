import logging
from sqlalchemy import text
from app.database.connection import engine

logger = logging.getLogger("ULTRON.Migration")

PHASE6_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS memory_embeddings (
        id VARCHAR(36) PRIMARY KEY,
        memory_id VARCHAR(36) NOT NULL,
        vector_json JSON NOT NULL,
        dimension INT NOT NULL DEFAULT 384,
        provider_name VARCHAR(100) NOT NULL DEFAULT 'mock',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
        INDEX idx_mem_embed_memory_id (memory_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS memory_links (
        id VARCHAR(36) PRIMARY KEY,
        source_memory_id VARCHAR(36) NOT NULL,
        target_memory_id VARCHAR(36) NOT NULL,
        link_type VARCHAR(50) NOT NULL DEFAULT 'related',
        strength FLOAT NOT NULL DEFAULT 1.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_memory_id) REFERENCES memories(id) ON DELETE CASCADE,
        FOREIGN KEY (target_memory_id) REFERENCES memories(id) ON DELETE CASCADE,
        INDEX idx_mem_links_source (source_memory_id),
        INDEX idx_mem_links_target (target_memory_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS memory_versions (
        id VARCHAR(36) PRIMARY KEY,
        memory_id VARCHAR(36) NOT NULL,
        version INT NOT NULL DEFAULT 1,
        content TEXT NOT NULL,
        importance INT NOT NULL DEFAULT 1,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        reason VARCHAR(255) NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
        INDEX idx_mem_versions_memory_id (memory_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS episodic_memories (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        conversation_id VARCHAR(36) NULL,
        execution_id VARCHAR(36) NOT NULL,
        goal TEXT NOT NULL,
        plan_json JSON NULL,
        agents_used_json JSON NULL,
        tools_used_json JSON NULL,
        execution_steps_json JSON NULL,
        failures_json JSON NULL,
        retries_count INT NOT NULL DEFAULT 0,
        duration_ms INT NOT NULL DEFAULT 0,
        final_result_json JSON NULL,
        review_result_json JSON NULL,
        success TINYINT(1) NOT NULL DEFAULT 1,
        lessons_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_ep_mem_user_id (user_id),
        INDEX idx_ep_mem_execution_id (execution_id),
        INDEX idx_ep_mem_success (success)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS semantic_memories (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        topic VARCHAR(255) NOT NULL,
        concept VARCHAR(255) NOT NULL,
        facts_json JSON NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        source VARCHAR(255) NOT NULL DEFAULT 'consolidation',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_sem_mem_user_id (user_id),
        INDEX idx_sem_mem_topic (topic)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS procedural_memories (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        workflow_name VARCHAR(255) NOT NULL,
        description TEXT NULL,
        trigger_conditions_json JSON NULL,
        steps_json JSON NOT NULL,
        agents_sequence_json JSON NULL,
        tools_sequence_json JSON NULL,
        success_rate FLOAT NOT NULL DEFAULT 1.0,
        sample_count INT NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_proc_mem_user_id (user_id),
        INDEX idx_proc_mem_workflow_name (workflow_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS preference_memories (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        `key` VARCHAR(255) NOT NULL,
        value TEXT NOT NULL,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        source VARCHAR(255) NOT NULL DEFAULT 'user_explicit',
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        INDEX idx_pref_mem_user_id (user_id),
        INDEX idx_pref_mem_key (`key`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS learning_events (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NULL,
        event_type VARCHAR(100) NOT NULL,
        observation_json JSON NULL,
        pattern_detected VARCHAR(255) NULL,
        action_taken_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE SET NULL,
        INDEX idx_learn_events_user_id (user_id),
        INDEX idx_learn_events_event_type (event_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS strategy_library (
        id VARCHAR(36) PRIMARY KEY,
        goal_type VARCHAR(100) NOT NULL,
        description TEXT NULL,
        steps_json JSON NOT NULL,
        agents_json JSON NULL,
        tools_json JSON NULL,
        success_rate FLOAT NOT NULL DEFAULT 1.0,
        sample_count INT NOT NULL DEFAULT 1,
        average_duration_ms INT NOT NULL DEFAULT 0,
        failure_rate FLOAT NOT NULL DEFAULT 0.0,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_strat_lib_goal_type (goal_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS strategy_results (
        id VARCHAR(36) PRIMARY KEY,
        strategy_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        success TINYINT(1) NOT NULL DEFAULT 1,
        duration_ms INT NOT NULL DEFAULT 0,
        feedback TEXT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (strategy_id) REFERENCES strategy_library(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_strat_res_strategy_id (strategy_id),
        INDEX idx_strat_res_execution_id (execution_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_metrics (
        id VARCHAR(36) PRIMARY KEY,
        agent_name VARCHAR(50) NOT NULL UNIQUE,
        total_runs INT NOT NULL DEFAULT 0,
        successful_runs INT NOT NULL DEFAULT 0,
        failed_runs INT NOT NULL DEFAULT 0,
        average_duration_ms INT NOT NULL DEFAULT 0,
        total_retries INT NOT NULL DEFAULT 0,
        tools_usage_json JSON NULL,
        average_review_score FLOAT NOT NULL DEFAULT 1.0,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_agent_metrics_name (agent_name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS execution_feedback (
        id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        execution_id VARCHAR(36) NOT NULL,
        rating INT NOT NULL DEFAULT 5,
        feedback_text TEXT NULL,
        corrected_output_json JSON NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
        INDEX idx_exec_fb_user_id (user_id),
        INDEX idx_exec_fb_execution_id (execution_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]


async def run_phase6_migrations():
    """Execute Phase 6 DDL statements to ensure tables exist in MySQL."""
    try:
        async with engine.begin() as conn:
            for sql in PHASE6_TABLES_SQL:
                await conn.execute(text(sql.strip()))
        logger.info("Phase 6 intelligence, memory, learning & strategy migration completed successfully.")
    except Exception as e:
        logger.warning(f"Phase 6 migration check notice: {e}")
