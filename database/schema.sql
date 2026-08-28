-- ULTRON Relational Schema for MySQL (Phase 1 + Phase 2 Execution Engine)
CREATE DATABASE IF NOT EXISTS ultron_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ultron_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_username (username),
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_token_hash (token_hash)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Conversations Table
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_conversations_user_id (user_id),
    INDEX idx_conversations_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_name VARCHAR(50) NOT NULL DEFAULT 'ULTRON',
    content LONGTEXT NOT NULL,
    metadata_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    INDEX idx_messages_conversation_id (conversation_id),
    INDEX idx_messages_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Memories Table
CREATE TABLE IF NOT EXISTS memories (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    memory_type VARCHAR(50) NOT NULL DEFAULT 'long_term',
    content TEXT NOT NULL,
    importance INT NOT NULL DEFAULT 1,
    metadata_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_memories_user_id (user_id),
    INDEX idx_memories_type (memory_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    due_date DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Agents Table
CREATE TABLE IF NOT EXISTS agents (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NULL,
    capabilities_json JSON NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_agents_code_name (code_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Agent Runs Table
CREATE TABLE IF NOT EXISTS agent_runs (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    input_prompt LONGTEXT NULL,
    output_result LONGTEXT NULL,
    execution_time_ms INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
    INDEX idx_agent_runs_conversation_id (conversation_id),
    INDEX idx_agent_runs_agent_id (agent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Tool Calls Table
CREATE TABLE IF NOT EXISTS tool_calls (
    id VARCHAR(36) PRIMARY KEY,
    agent_run_id VARCHAR(36) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    input_params_json JSON NULL,
    output_result_json JSON NULL,
    requires_approval TINYINT(1) NOT NULL DEFAULT 0,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'auto_approved',
    execution_time_ms INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_run_id) REFERENCES agent_runs(id) ON DELETE CASCADE,
    INDEX idx_tool_calls_agent_run_id (agent_run_id),
    INDEX idx_tool_calls_tool_name (tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    permission_level VARCHAR(50) NOT NULL DEFAULT 'allow',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_tool (user_id, tool_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255) NULL,
    details_json JSON NULL,
    ip_address VARCHAR(50) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_logs_user_id (user_id),
    INDEX idx_audit_logs_action (action),
    INDEX idx_audit_logs_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================
-- PHASE 2 EXTENSIONS: EXECUTION ENGINE, TASK GRAPH & APPROVAL TABLES
-- =========================================================================

-- 12. Executions Table (Top-level goal execution instance)
CREATE TABLE IF NOT EXISTS executions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    conversation_id VARCHAR(36) NULL,
    goal TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, PAUSED
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE SET NULL,
    INDEX idx_executions_user_id (user_id),
    INDEX idx_executions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Execution Tasks Table (Task Graph DAG Nodes)
CREATE TABLE IF NOT EXISTS execution_tasks (
    id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    goal VARCHAR(255) NOT NULL,
    description TEXT NULL,
    assigned_agent VARCHAR(50) NOT NULL DEFAULT 'commander',
    dependencies_json JSON NULL, -- List of prerequisite task IDs
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, RUNNING, WAITING, COMPLETED, FAILED, CANCELLED, REQUIRES_APPROVAL
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    input_json JSON NULL,
    output_json JSON NULL,
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    INDEX idx_exec_tasks_execution_id (execution_id),
    INDEX idx_exec_tasks_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. Execution Events Table (Structured event log for timeline & WebSockets)
CREATE TABLE IF NOT EXISTS execution_events (
    id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    INDEX idx_exec_events_execution_id (execution_id),
    INDEX idx_exec_events_event_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. Approvals Table (Backend validated tool approvals)
CREATE TABLE IF NOT EXISTS approvals (
    id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    tool_name VARCHAR(100) NOT NULL,
    params_json JSON NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, approved, denied
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES execution_tasks(id) ON DELETE CASCADE,
    INDEX idx_approvals_execution_id (execution_id),
    INDEX idx_approvals_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================
-- PHASE 3 EXTENSIONS: BROWSER SESSIONS, ACTIONS, PAGES & RESEARCH SOURCES
-- =========================================================================

-- 16. Browser Sessions Table
CREATE TABLE IF NOT EXISTS browser_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NULL,
    current_url VARCHAR(2048) NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, CLOSED, ERROR
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE SET NULL,
    INDEX idx_browser_sessions_user_id (user_id),
    INDEX idx_browser_sessions_execution_id (execution_id),
    INDEX idx_browser_sessions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 17. Browser Actions Table
CREATE TABLE IF NOT EXISTS browser_actions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    params_json JSON NULL,
    result_json JSON NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'SUCCESS', -- SUCCESS, FAILED, REQUIRES_APPROVAL
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES browser_sessions(id) ON DELETE CASCADE,
    INDEX idx_browser_actions_session_id (session_id),
    INDEX idx_browser_actions_action_type (action_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 18. Browser Pages Table
CREATE TABLE IF NOT EXISTS browser_pages (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    title VARCHAR(512) NULL,
    page_structure_json JSON NULL,
    captured_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES browser_sessions(id) ON DELETE CASCADE,
    INDEX idx_browser_pages_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 19. Research Sources Table
CREATE TABLE IF NOT EXISTS research_sources (
    id VARCHAR(36) PRIMARY KEY,
    execution_id VARCHAR(36) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    url VARCHAR(2048) NOT NULL,
    title VARCHAR(512) NULL,
    domain VARCHAR(255) NULL,
    summary_json JSON NULL,
    retrieved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    INDEX idx_research_sources_execution_id (execution_id),
    INDEX idx_research_sources_domain (domain)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================
-- PHASE 4 EXTENSIONS: CODE INTELLIGENCE & EXECUTION SANDBOX TABLES
-- =========================================================================

-- 20. Code Workspaces Table
CREATE TABLE IF NOT EXISTS code_workspaces (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NULL,
    task_id VARCHAR(36) NULL,
    name VARCHAR(255) NOT NULL DEFAULT 'default_workspace',
    root_path VARCHAR(1024) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE SET NULL,
    INDEX idx_code_workspaces_user_id (user_id),
    INDEX idx_code_workspaces_execution_id (execution_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 21. Code Files Table
CREATE TABLE IF NOT EXISTS code_files (
    id VARCHAR(36) PRIMARY KEY,
    workspace_id VARCHAR(36) NOT NULL,
    path VARCHAR(1024) NOT NULL,
    language VARCHAR(50) NOT NULL DEFAULT 'text',
    content LONGTEXT NULL,
    size_bytes INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES code_workspaces(id) ON DELETE CASCADE,
    INDEX idx_code_files_workspace_id (workspace_id),
    INDEX idx_code_files_path (path(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 22. Code Executions Table
CREATE TABLE IF NOT EXISTS code_executions (
    id VARCHAR(36) PRIMARY KEY,
    workspace_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    agent VARCHAR(50) NOT NULL DEFAULT 'code_agent',
    runtime VARCHAR(50) NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'CREATED',
    exit_code INT NULL,
    stdout LONGTEXT NULL,
    stderr LONGTEXT NULL,
    duration_ms INT NULL,
    retry_count INT NOT NULL DEFAULT 0,
    cpu_usage_user_ms INT NULL,
    memory_usage_mb INT NULL,
    output_size_bytes INT NULL,
    artifact_count INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME NULL,
    FOREIGN KEY (workspace_id) REFERENCES code_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_code_executions_workspace_id (workspace_id),
    INDEX idx_code_executions_execution_id (execution_id),
    INDEX idx_code_executions_user_id (user_id),
    INDEX idx_code_executions_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 23. Code Execution Events Table
CREATE TABLE IF NOT EXISTS code_execution_events (
    id VARCHAR(36) PRIMARY KEY,
    code_execution_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_execution_id) REFERENCES code_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    INDEX idx_code_exec_events_code_exec_id (code_execution_id),
    INDEX idx_code_exec_events_execution_id (execution_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 24. Code Artifacts Table
CREATE TABLE IF NOT EXISTS code_artifacts (
    id VARCHAR(36) PRIMARY KEY,
    code_execution_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL DEFAULT 'text/plain',
    size_bytes INT NOT NULL DEFAULT 0,
    hash_sha256 VARCHAR(64) NULL,
    sandbox_path VARCHAR(1024) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_execution_id) REFERENCES code_executions(id) ON DELETE CASCADE,
    FOREIGN KEY (execution_id) REFERENCES executions(id) ON DELETE CASCADE,
    INDEX idx_code_artifacts_code_exec_id (code_execution_id),
    INDEX idx_code_artifacts_execution_id (execution_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 25. Code Tests Table
CREATE TABLE IF NOT EXISTS code_tests (
    id VARCHAR(36) PRIMARY KEY,
    code_execution_id VARCHAR(36) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    output LONGTEXT NULL,
    duration_ms INT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (code_execution_id) REFERENCES code_executions(id) ON DELETE CASCADE,
    INDEX idx_code_tests_code_exec_id (code_execution_id),
    INDEX idx_code_tests_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================================
-- PHASE 5 EXTENSIONS: PERCEPTION ENGINE & CONTROLLED COMPUTER INTERACTION
-- =========================================================================

-- 26. Computer Sessions Table
CREATE TABLE IF NOT EXISTS computer_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, CLOSED, EXPIRED, CANCELLED
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

-- 27. Computer Screenshots Table
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

-- 28. Perception Results Table
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

-- 29. Computer Actions Table
CREATE TABLE IF NOT EXISTS computer_actions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- MOVE, CLICK, DOUBLE_CLICK, RIGHT_CLICK, TYPE, PRESS_KEY, HOTKEY, SCROLL, DRAG, WAIT, SCREENSHOT
    target_json JSON NULL,
    parameters_json JSON NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, APPROVED, EXECUTING, COMPLETED, FAILED, REJECTED, CANCELLED
    approval_state VARCHAR(50) NOT NULL DEFAULT 'AUTO_APPROVED', -- AUTO_APPROVED, REQUIRES_APPROVAL, APPROVED, REJECTED
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

-- =========================================================================
-- PHASE 6 EXTENSIONS: PERSISTENT INTELLIGENCE, MEMORY & STRATEGY
-- =========================================================================

-- 30. Memory Embeddings Table
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

-- 31. Memory Links Table
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

-- 32. Memory Versions Table
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

-- 33. Episodic Memories Table
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

-- 34. Semantic Memories Table
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

-- 35. Procedural Memories Table
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

-- 36. Preference Memories Table
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

-- 37. Learning Events Table
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

-- 38. Strategy Library Table
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

-- 39. Strategy Results Table
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

-- 40. Agent Metrics Table
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

-- 41. Execution Feedback Table
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

-- =========================================================================
-- PHASE 7 EXTENSIONS: AUTONOMOUS ORCHESTRATION & WORKFLOW ENGINE
-- =========================================================================

CREATE TABLE IF NOT EXISTS workflows (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    execution_id VARCHAR(36) NULL,
    goal TEXT NOT NULL,
    strategy_id VARCHAR(36) NULL,
    current_state VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    progress FLOAT NOT NULL DEFAULT 0.0,
    current_step VARCHAR(64) NULL,
    retry_count INT NOT NULL DEFAULT 0,
    replan_count INT NOT NULL DEFAULT 0,
    metadata_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_workflows_user_id (user_id),
    INDEX idx_workflows_state (current_state)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_steps (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    step_id VARCHAR(64) NOT NULL,
    name VARCHAR(255) NOT NULL,
    assigned_agent VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    dependencies_json JSON NULL,
    input_data_json JSON NULL,
    output_data_json JSON NULL,
    error_message TEXT NULL,
    retry_count INT NOT NULL DEFAULT 0,
    duration_ms INT NOT NULL DEFAULT 0,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_steps_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_events (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_events_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    checkpoint_name VARCHAR(128) NOT NULL,
    state_snapshot_json JSON NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_checkpoints_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_failures (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(64) NULL,
    agent VARCHAR(64) NULL,
    failure_type VARCHAR(64) NOT NULL,
    error_message TEXT NOT NULL,
    context_json JSON NULL,
    recoverable TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_failures_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_approvals (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    task_id VARCHAR(64) NOT NULL,
    action_type VARCHAR(64) NOT NULL,
    details_json JSON NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING',
    decided_by VARCHAR(36) NULL,
    decided_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_approvals_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_results (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    summary TEXT NOT NULL,
    status VARCHAR(32) NOT NULL,
    confidence FLOAT NOT NULL DEFAULT 1.0,
    evidence_json JSON NULL,
    tasks_completed INT NOT NULL DEFAULT 0,
    tasks_failed INT NOT NULL DEFAULT 0,
    warnings_json JSON NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_results_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS workflow_artifacts (
    id VARCHAR(36) PRIMARY KEY,
    workflow_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    artifact_type VARCHAR(64) NOT NULL,
    size_bytes INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id) ON DELETE CASCADE,
    INDEX idx_wf_artifacts_workflow_id (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;





