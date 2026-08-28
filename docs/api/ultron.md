# Phase 10 Unified Command REST API Specifications

`Base Path: /api/v1/ultron`

### Endpoints
- `POST /command` — Execute unified natural language user command ("ULTRON, handle this"). Converts prompt into an autonomous workflow DAG.
- `GET /status` — Get system status, operating system version, and capability health.
- `GET /capabilities` — List registered system capabilities and health status.
- `GET /timeline` — Retrieve live unified activity stream timeline.
