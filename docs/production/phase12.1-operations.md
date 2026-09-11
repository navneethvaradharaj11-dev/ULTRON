# PROJECT ULTRON — PHASE 12.1 OPERATIONS & INCIDENT RUNBOOK

---

## 1. Daily Operations & Monitoring

* **Liveness Probe**: `GET /health/live` (monitored by container orchestrator / uptime check every 30s).
* **Readiness Probe**: `GET /health/ready` (verifies MySQL, Redis, Sandbox storage readiness).
* **Metrics Monitoring**: `GET /metrics` (scraped by Prometheus / Grafana dashboard).

---

## 2. Emergency Recovery Runbook

### Scenario A: Backend API Unresponsive
```bash
docker-compose restart backend worker
```

### Scenario B: Database Degradation / Lockup
```bash
docker-compose exec mysql mysqladmin ping -u ultron_user -p
docker-compose restart mysql
```

### Scenario C: Rollback Container Tag
```bash
bash scripts/rollback.sh v11.0.0
```
