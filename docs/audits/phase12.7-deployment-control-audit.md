# PROJECT ULTRON — PHASE 12.7 DEPLOYMENT CONTROL AUDIT

---

## 1. Single Source of Truth Configuration Strategy

The deployment configuration strategy centralizes environment variable resolution and security policy assertion inside `backend/app/config/settings.py` and `.env.production.example`.

### Key Parameters & Boundaries
- **Environment**: `development`, `staging`, `production`.
- **Secrets**: `JWT_SECRET` (must be >= 32 bytes and non-default in production), `MYSQL_PASSWORD` (default `root` prohibited in production).
- **Network Boundaries**: `HOST`, `PORT`, `CORS_ALLOWED_ORIGINS` (wildcard `*` prohibited in production mode).
- **Execution Resource Limits**: Memory limits (1536M backend, 1024M worker, 1024M MySQL), CPU limits, code execution timeouts.

---

## 2. Production Environment Validator (`preflight.py`)

The pre-flight validator executes fail-closed checks before any deployment stage begins:
1. Asserts `ENVIRONMENT=production` does not run with `DEBUG=True`.
2. Asserts `JWT_SECRET` is strong (length >= 32 bytes, no default strings).
3. Asserts `MYSQL_PASSWORD` is non-default.
4. Asserts `CORS_ALLOWED_ORIGINS` is restricted.
5. Verifies required filesystem workspace directories (`/opt/ultron/backups`, `/opt/ultron/logs`, `sandbox`).
6. Asserts Docker binary availability.

---

## 3. Deployment State Machine Automation (`ultronctl.sh`)

The Zero-to-Live deployment pipeline enforces a 10-stage sequential state model:

```text
  [PRECHECK]       --> Runs preflight.py (Fail Closed)
       ↓
   [BACKUP]        --> Runs backup.sh to preserve database state
       ↓
    [BUILD]        --> Builds docker stack without cache
       ↓
   [MIGRATE]       --> Executes idempotent schema migrations
       ↓
    [DEPLOY]       --> Launches container stack (mysql, redis, backend, worker, proxy)
       ↓
  [HEALTHCHECK]    --> Validates /health/live and /health/ready probes
       ↓
  [HTTPS CHECK]    --> Validates TLS security rules & HTTP->HTTPS redirect
       ↓
   [WSS CHECK]     --> Validates WebSocket upgrade handlers
       ↓
  [SMOKE TEST]     --> Runs smoke_test.py suite
       ↓
    [READY]        --> Stack declared OPERATIONAL
       │
       └─── (If any mandatory stage fails) ──> [ROLLBACK] (Triggers rollback.sh)
```

---

## 4. Operator CLI Specification (`ultronctl.sh`)

| Command | Action Performed | Return Behavior |
| :--- | :--- | :--- |
| `./ultronctl.sh preflight` | Executes `preflight.py` validation checks. | Exits 0 on pass, 1 on fail-closed error. |
| `./ultronctl.sh backup` | Creates timestamped gzipped MySQL database backup. | Outputs backup filepath. |
| `./ultronctl.sh deploy` | Executes the 10-stage deployment state machine. | Triggers `rollback.sh` on failure. |
| `./ultronctl.sh status` | Displays container status and system mode. | Outputs status matrix. |
| `./ultronctl.sh health` | Queries `/health/live` and `/health/ready` probes. | Displays component health statuses. |
| `./ultronctl.sh logs` | Tails live container log streams. | Streams logs to stdout. |
| `./ultronctl.sh smoke-test` | Runs endpoint smoke tests against target host. | Returns summary count. |
| `./ultronctl.sh rollback` | Invokes `rollback.sh` to restore previous stack state. | Restores baseline container state. |
| `./ultronctl.sh restore` | Restores database from specified backup file. | Restores MySQL database. |

---

## 5. Audit Verdict

**DEPLOYMENT CONTROL AUDIT VERDICT**: **PASS** (Control center, validators, and state machine fully operational).
