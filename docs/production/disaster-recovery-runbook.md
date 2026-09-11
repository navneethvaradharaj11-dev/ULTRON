# PROJECT ULTRON — DISASTER RECOVERY RUNBOOK

---

## 1. Disaster Recovery Matrix

| Failure Scenario | Initial Diagnosis | Remediation Action | Recovery SLA |
| :--- | :--- | :--- | :---: |
| **MySQL Database Corruption** | `/health/ready` returns `database: unhealthy` | Run `python scripts/backup_restore.py --test-restore` to restore latest backup snapshot | < 5 mins |
| **Redis Queue Crash** | Background workers fail to pick up jobs | Restart Redis container: `docker-compose restart redis` | < 1 min |
| **Background Worker Failure** | Job queue backing up (`queue:default`) | Restart worker process: `docker-compose restart worker` | < 1 min |
| **FastAPI Backend Crash** | REST API returns 502 / 503 | `docker-compose restart backend` | < 30 secs |
| **Nginx Proxy Lockup** | HTTP / HTTPS traffic timing out | `docker-compose restart proxy` | < 15 secs |
| **Host VM Failure** | All containers unreachable | Provision new VM instance, pull containers, mount backup volume | < 15 mins |
| **Secret Compromise** | Unauthorized JWT token usage detected | Rotate `JWT_SECRET` in `.env`, restart stack to invalidate all active tokens | < 2 mins |
| **Corrupted Code Artifact** | Sandbox execution throws syntax error | Flush scratch cache: `rm -rf scratch/*` | Immediate |
| **Failed Deployment** | Staging / Prod container fails healthcheck | Execute rollback script: `bash scripts/rollback.sh <prev_tag>` | < 3 mins |

---

## 2. Emergency Backup & Restore Commands

### Create On-Demand Backup Snapshot
```bash
python scripts/backup_restore.py
```

### Perform Automated Restore Verification Test
```bash
python scripts/backup_restore.py --test-restore
```
