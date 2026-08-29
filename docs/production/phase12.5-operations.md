# PROJECT ULTRON — OPERATIONAL MANUAL

---

## 1. Operational Runbook

### Health Monitoring

```bash
# Liveness Probe
curl http://localhost:8000/health/live

# Readiness Probe
curl http://localhost:8000/health/ready

# Prometheus Metrics
curl http://localhost:8000/api/v1/metrics
```

### Log Inspection

```bash
# View all container logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend
```

### Automated Database Backups

```bash
# Trigger manual backup
bash ./scripts/deploy/backup.sh
```
