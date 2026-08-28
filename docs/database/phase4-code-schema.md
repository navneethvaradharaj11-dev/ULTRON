# Phase 4 Database Schema Documentation

## MySQL Relational Tables

### 1. `code_workspaces`
- `id` (VARCHAR(36), PK)
- `user_id` (VARCHAR(36), FK users.id)
- `execution_id` (VARCHAR(36), FK executions.id)
- `task_id` (VARCHAR(36))
- `name` (VARCHAR(255))
- `root_path` (VARCHAR(1024))
- `status` (VARCHAR(50))
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

### 2. `code_files`
- `id` (VARCHAR(36), PK)
- `workspace_id` (VARCHAR(36), FK code_workspaces.id)
- `path` (VARCHAR(1024))
- `language` (VARCHAR(50))
- `content` (LONGTEXT)
- `size_bytes` (INT)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

### 3. `code_executions`
- `id` (VARCHAR(36), PK)
- `workspace_id` (VARCHAR(36), FK code_workspaces.id)
- `execution_id` (VARCHAR(36), FK executions.id)
- `task_id` (VARCHAR(36))
- `user_id` (VARCHAR(36), FK users.id)
- `agent` (VARCHAR(50))
- `runtime` (VARCHAR(50))
- `language` (VARCHAR(50))
- `status` (VARCHAR(50))
- `exit_code` (INT)
- `stdout` (LONGTEXT)
- `stderr` (LONGTEXT)
- `duration_ms` (INT)
- `retry_count` (INT)
- `cpu_usage_user_ms` (INT)
- `memory_usage_mb` (INT)
- `output_size_bytes` (INT)
- `artifact_count` (INT)
- `created_at` (DATETIME)
- `completed_at` (DATETIME)

### 4. `code_execution_events`
- `id` (VARCHAR(36), PK)
- `code_execution_id` (VARCHAR(36), FK code_executions.id)
- `execution_id` (VARCHAR(36), FK executions.id)
- `event_type` (VARCHAR(100))
- `payload_json` (JSON)
- `created_at` (DATETIME)

### 5. `code_artifacts`
- `id` (VARCHAR(36), PK)
- `code_execution_id` (VARCHAR(36), FK code_executions.id)
- `execution_id` (VARCHAR(36), FK executions.id)
- `task_id` (VARCHAR(36))
- `filename` (VARCHAR(255))
- `mime_type` (VARCHAR(100))
- `size_bytes` (INT)
- `hash_sha256` (VARCHAR(64))
- `sandbox_path` (VARCHAR(1024))
- `created_at` (DATETIME)

### 6. `code_tests`
- `id` (VARCHAR(36), PK)
- `code_execution_id` (VARCHAR(36), FK code_executions.id)
- `test_name` (VARCHAR(255))
- `framework` (VARCHAR(50))
- `status` (VARCHAR(50))
- `output` (LONGTEXT)
- `duration_ms` (INT)
- `created_at` (DATETIME)
