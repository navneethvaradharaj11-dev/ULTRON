# Memory Engine Documentation

## Memory Schema & Categories
Every memory contains:
- `id`: Unique UUID
- `user_id`: Multi-tenant ownership
- `type`: `WORKING`, `EPISODIC`, `SEMANTIC`, `PROCEDURAL`, or `PREFERENCE`
- `content`: Text description
- `importance`: Integer (1 to 5)
- `confidence`: Float (0.0 to 1.0)
- `source`: Origin (`user`, `consolidation`, `learning_agent`)
- `created_at`, `updated_at`, `last_accessed`
- `access_count`: Frequency counter
- `status`: `ACTIVE`, `FORGOTTEN`

## Retrieval & Ranking Pipeline
1. Candidate retrieval for `user_id` and category.
2. Ranking equation:
   `score = (relevance * 0.40) + (recency * 0.20) + (importance/5.0 * 0.20) + (confidence * 0.20)`
3. Top `k` memories returned to Context Engine.
