# PROJECT ULTRON — Operations, Monitoring & Runbook

This runbook guides operators on managing, monitoring, backing up, and maintaining PROJECT ULTRON Phase 12.8 in production.

---

## 1. Daily Operator Cheatsheet (`ultronctl.sh`)

| Task | Command | Description |
| :--- | :--- | :--- |
| **System Status** | `./scripts/ultronctl.sh status` | Show container health, CPU/RAM, and OS version |
| **Liveness & Probes** | `./scripts/ultronctl.sh health` | Query `/health/live`, `/health/ready`, and status |
| **Tail Logs** | `./scripts/ultronctl.sh logs` | Follow live container logs across backend, worker, mysql, redis, proxy |
| **Smoke Test** | `./scripts/ultronctl.sh smoke-test` | Execute end-to-end endpoint verification probe |
| **Backup State** | `./scripts/ultronctl.sh backup` | Dump MySQL & database state to gzipped archive |
| **Rollback** | `./scripts/ultronctl.sh rollback` | Revert to previous container deployment state |
| **Restore** | `./scripts/ultronctl.sh restore <file>` | Restore database from backup archive |

---

## 2. Health & Monitoring Probes

ULTRON exposes standardized observability endpoints:

- **Liveness Probe**: `GET /health/live`
  - Returns `{"status": "alive"}` (HTTP 200).
- **Readiness Probe**: `GET /health/ready`
  - Validates MySQL connection and Redis availability.
  - Returns `{"status": "ready"}` (HTTP 200) or HTTP 503 if dependencies fail.
- **Metrics Exposition**: `GET /api/v1/metrics`
  - Standard Prometheus-formatted metrics:
    - `ultron_requests_total`
    - `ultron_workflow_executions_total`
    - `ultron_active_agents`
    - `ultron_memory_bytes`
- **System Health Status**: `GET /api/v1/health`
  - Detailed report on capabilities, database status, redis state, and emergency shutdown status.

---

## 3. Automated Backup Procedure

Run automated backup:
```bash
./scripts/ultronctl.sh backup
```

Backups are saved to `/opt/ultron/backups/ultron_backup_YYYYMMDD_HHMMSS.sql.gz`.

### Recommended Cron Setup for Daily Backups
Add to server crontab (`crontab -e`):
```cron
# Run daily ULTRON database backup at 02:00 UTC
0 2 * * * cd /opt/ultron && ./scripts/ultronctl.sh backup >> /opt/ultron/logs/backup.log 2>&1
```

---

## 4. Disaster Recovery & Database Restoration

In the event of database corruption or hardware failure:

1. **Stop active services**:
   ```bash
   docker compose down
   ```
2. **Restore database snapshot**:
   ```bash
   ./scripts/ultronctl.sh restore /opt/ultron/backups/ultron_backup_YYYYMMDD_HHMMSS.sql.gz
   ```
3. **Restart containers & verify**:
   ```bash
   ./scripts/ultronctl.sh deploy
   ./scripts/ultronctl.sh health
   ```

---

## 5. Emergency Circuit Breaker

If an agent or integration behaves unexpectedly:
```bash
curl -X POST http://localhost:8000/api/v1/ultron/emergency-shutdown \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Operator requested emergency circuit-break"}'
```

This immediately halts all background triggers, pauses task dispatch, and logs the incident.

---

## 6. Tailscale Mesh & Local WSL2 Operations

### Checking Tailscale Bridge Status
The Tailscale bridge forwards incoming traffic on the Tailscale IP (`100.69.161.16:8000`) directly to the WSL2 Docker backend:
```cmd
python scripts\tailscale_bridge.py
```

### Probing Port Isolation & Security Boundaries
Verify that MySQL (3306) and Redis (6379) are strictly isolated from external and Tailscale access:
```cmd
curl.exe --max-time 2 http://100.69.161.16:3306
curl.exe --max-time 2 http://100.69.161.16:6379
```
*Expected Result*: Connection timed out (refused / inaccessible).

### Verifying WSL2 Auto-Recovery
When WSL2 or Docker containers restart:
1. Docker restart policy `restart: unless-stopped` automatically boots MySQL, Redis, Backend, Worker, and Proxy.
2. The Tailscale bridge (`scripts/tailscale_bridge.py`) dynamically detects the new WSL2 IP and resumes traffic flow with zero data loss.
3. Validate API health via Tailscale:
```cmd
curl.exe -f http://100.69.161.16:8000/health
```
