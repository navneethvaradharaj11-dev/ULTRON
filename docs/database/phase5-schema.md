# Phase 5 Database Schema (MySQL Persistence)

## Tables Added

### 1. `computer_sessions`
- `id` (VARCHAR 36, PK)
- `user_id` (VARCHAR 36, FK users.id)
- `execution_id` (VARCHAR 36, FK executions.id)
- `viewport_width` (INT)
- `viewport_height` (INT)
- `status` (VARCHAR 50)
- `action_count` (INT)
- `created_at`, `closed_at` (DATETIME)

### 2. `computer_screenshots`
- `id` (VARCHAR 36, PK)
- `session_id` (VARCHAR 36, FK computer_sessions.id)
- `file_path` (VARCHAR 512)
- `width`, `height` (INT)
- `captured_at` (DATETIME)

### 3. `perception_results`
- `id` (VARCHAR 36, PK)
- `session_id` (VARCHAR 36, FK computer_sessions.id)
- `execution_id` (VARCHAR 36)
- `elements_json` (JSON)
- `confidence` (FLOAT)
- `ocr_text` (TEXT)
- `created_at` (DATETIME)

### 4. `computer_actions`
- `id` (VARCHAR 36, PK)
- `session_id` (VARCHAR 36, FK computer_sessions.id)
- `action_type` (VARCHAR 50)
- `target_json` (JSON)
- `parameters_json` (JSON)
- `status` (VARCHAR 50)
- `approval_state` (VARCHAR 50)
- `created_at` (DATETIME)
