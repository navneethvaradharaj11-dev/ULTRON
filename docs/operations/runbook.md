# PROJECT ULTRON — Operations & Maintenance Runbook

## 1. System Health Diagnostics
- **REST Health Check**: `GET /health` (returns database connection status and registered tools count).
- **Capability Health Check**: `GET /api/v1/ultron/status` (returns OS version, system health status, total capabilities count, and active capabilities list).

---

## 2. Emergency Recovery & Incident Response
- **Workflow Stagnation**: If a workflow stalls due to network interruption, invoke `POST /api/v1/workflows/{id}/resume` or trigger automated replanning.
- **Revoking Compromised Tokens**: Call `TokenBlacklist.revoke_token(token)` to immediately invalidate user access tokens.
- **Process Sandbox Clearing**: Temp sandbox workspace directories under `sandbox/` can be safely purged; persistent artifacts remain recorded in MySQL.
