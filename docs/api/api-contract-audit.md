# PROJECT ULTRON — API CONTRACT AUDIT REPORT

---

## 1. REST & WebSocket API Endpoint Matrix

| Endpoint Group | Router Path | Auth Requirement | Tenant Isolation | Rate Limiting | Audit Findings |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Health Probes** | `/health`, `/health/live`, `/health/ready` | None (Public Probe) | N/A | Exempt | Returns container liveness & deep readiness status. |
| **Metrics** | `/api/v1/metrics` | None (Operator Probe) | N/A | Exempt | Prometheus formatted text metrics output. |
| **Feedback** | `/api/v1/feedback` | Bearer JWT | Enforced | 60 req/min | Accepts user bug reports with correlation tracing. |
| **Auth** | `/api/v1/auth/login`, `/register` | Public / Token | N/A | 10 req/min | Issues access (24h) and refresh (7d) tokens. |
| **Ultron Core** | `/api/v1/ultron/command` | Bearer JWT | Enforced | 60 req/min | Dispatches user commands to `UltronCore`. |
| **Workflows** | `/api/v1/workflows` | Bearer JWT | Enforced | 60 req/min | Creates, lists, pauses, resumes, and cancels DAG workflows. |
| **Knowledge** | `/api/v1/knowledge/ingest` | Bearer JWT | Enforced | 30 req/min | Ingests PDF, CSV, DOCX, MD, Code into vector store. |
| **Memory** | `/api/v1/memory` | Bearer JWT | Enforced | 60 req/min | Retrieves, creates, and sanitizes long-term memory. |
| **Autonomy** | `/api/v1/autonomy/rules` | Bearer JWT | Enforced | 60 req/min | Manages autonomous trigger rules and event logs. |
| **WebSocket** | `/ws/chat/{conversation_id}` | Query Token | Enforced | WS Limit | Live streaming chat & thinking indicators. |

---

## 2. API Contract Verification Summary

All REST and WebSocket endpoints enforce **JSON request validation**, **tenant isolation (`user_id`)**, **correlation ID propagation (`X-Correlation-ID`)**, **secret redaction**, and **fail-closed status codes (`401`, `403`, `404`, `422`, `500`)**.
