# Memory REST API Documentation

## Endpoints
- `POST /api/v1/memory`: Create memory
- `GET /api/v1/memory`: List user memories (filter by `type`)
- `GET /api/v1/memory/{id}`: Get memory details
- `POST /api/v1/memory/search`: Keyword search
- `POST /api/v1/memory/semantic-search`: Relevance & ranking search
- `POST /api/v1/memory/consolidate`: Consolidate observations
- `POST /api/v1/memory/{id}/forget`: Soft-delete memory
- `DELETE /api/v1/memory/{id}`: Hard-delete memory
