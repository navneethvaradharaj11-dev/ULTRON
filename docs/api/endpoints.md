# ULTRON API Reference

## Health Check
- `GET /health`: Returns system status, MySQL database connection state, AI provider status, and registered tool counts.

## Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register`: Create user account (`username`, `email`, `password`).
- `POST /api/v1/auth/login`: Authenticate user and issue JWT bearer token.
- `GET /api/v1/auth/me`: Get current authenticated user profile.

## Chat & Conversations (`/api/v1/chat`)
- `POST /api/v1/chat/conversations`: Start new conversation.
- `GET /api/v1/chat/conversations`: List active conversations for authenticated user.
- `GET /api/v1/chat/conversations/{id}/messages`: Get message history for authorized conversation.

## WebSocket Streaming (`/ws/chat/{conversation_id}?token={jwt_token}`)
- Real-time event protocol streaming `message_start`, `agent_started`, `agent_progress`, `tool_started`, `tool_completed`, `approval_required`, `message_delta`, `message_complete`.

## Long-Term Memory (`/api/v1/memory`)
- `POST /api/v1/memory/`: Create long-term memory.
- `GET /api/v1/memory/`: List user memories.
- `DELETE /api/v1/memory/{id}`: Delete specific memory.

## Tasks (`/api/v1/tasks`)
- `POST /api/v1/tasks/`: Create task.
- `GET /api/v1/tasks/`: List user tasks.
- `PATCH /api/v1/tasks/{id}/status`: Update task status.
