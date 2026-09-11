# PROJECT ULTRON — BETA RELEASE CHECKLIST

---

## 1. Environment & Infrastructure Checklist

- [x] `ENVIRONMENT=production` and `DEBUG=False` set in `.env`.
- [x] `settings.validate_production_secrets()` verified (fails closed if default `JWT_SECRET` is used).
- [x] Multi-stage non-root `Dockerfile` verified (`ultron:ultron`).
- [x] `docker-compose.yml` operational (`backend`, `worker`, `mysql`, `redis`, `proxy`).
- [x] Nginx proxy SSL termination & WebSocket `Upgrade` header forwarding configured.
- [x] Database migration tracking `schema_migrations` verified for idempotency.
- [x] Redis worker queue `queue:default` and Dead-Letter Queue (DLQ) verified.
- [x] Automated backup script `scripts/backup_restore.py` and restore verification test verified.
- [x] Container rollback script `scripts/rollback.sh` verified.

---

## 2. Security & Privacy Checklist

- [x] Fail-closed authentication (JWT validation on REST and WebSocket endpoints).
- [x] Multi-tenant isolation strictly enforced across all database queries (`user_id`).
- [x] Secret detector auto-strips credentials from long-term memory and logs.
- [x] Playwright Chromium SSRF private IP & metadata endpoint protection verified.
- [x] Python sandbox process jail timeout (30s) and path traversal protection verified.
- [x] Human approval gates enforced on all sensitive write operations (`APPROVE` vs. `DENY`).

---

## 3. Product & User Experience Checklist

- [x] Flutter client builds cleanly with zero errors (`flutter analyze`).
- [x] Configurable `--dart-define=API_BASE_URL=...` for mobile release builds.
- [x] Network retry wrapper in `ApiService` and auto-reconnecting `WebSocketService`.
- [x] User feedback and bug report submission endpoint `/api/v1/feedback` operational.
- [x] Zero raw stack traces or internal filesystem paths exposed in error messages.
