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
