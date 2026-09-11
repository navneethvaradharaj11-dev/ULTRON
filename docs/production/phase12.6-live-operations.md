# PROJECT ULTRON — PHASE 12.6 LIVE OPERATIONS MANUAL

---

## 1. Overview & Operating Architecture

This document provides operational instructions for managing, monitoring, backing up, restoring, and rolling back the ULTRON Autonomous Multi-Agent Platform on a production Cloud VPS environment.

---

## 2. One-Command Infrastructure Provisioning

To provision a fresh Ubuntu 22.04 / 24.04 LTS VPS instance:

```bash
# 1. SSH into VPS as root
ssh root@<VPS_PUBLIC_IPV4>

# 2. Clone ULTRON production repository
git clone https://github.com/ultron-ai/ULTRON.git /opt/ultron
cd /opt/ultron

# 3. Create production environment file with secure secrets
cp .env.production.example /opt/ultron/.env.production
nano /opt/ultron/.env.production # Populate secure JWT_SECRET and MYSQL_PASSWORD

# 4. Execute Bootstrap Automation
bash ./scripts/deploy/bootstrap.sh
```

---

## 3. Deployment & Zero-Downtime Updates

To deploy or update running services:

```bash
cd /opt/ultron
bash ./scripts/deploy/deploy.sh
```

The script performs:
1. Container image building without cache.
2. MySQL and Redis initialization.
3. Database migrations (`python -m app.database.migrate`).
4. Full stack startup (`backend`, `worker`, `mysql`, `redis`, `proxy`).
5. Live probe (`/health/live`) and readiness probe (`/health/ready`) verification.
6. Automatic rollback invocation if health checks fail within timeout.

---

## 4. HTTPS & Domain SSL Management

To provision or renew Let's Encrypt TLS certificates:

```bash
bash ./scripts/deploy/setup_https.sh <DOMAIN_NAME> <ADMIN_EMAIL>
```

- Automatic renewal cron is installed and verified via `certbot renew --dry-run`.

---

## 5. Security & Firewall Hardening

To enforce UFW firewall rules on the production host:

```bash
bash ./scripts/deploy/setup_firewall.sh
```

- Allowed Public Ports: `80` (HTTP), `443` (HTTPS), `22` (SSH).
- Blocked Public Ports: `3306` (MySQL), `6379` (Redis), `8000` (FastAPI backend), `9222` (Playwright debug).

---

## 6. Database Backup & Disaster Recovery

### A. Automated Backup
```bash
bash ./scripts/deploy/backup.sh
```
- Backups are dumped to `/opt/ultron/backups/ultron_backup_<TIMESTAMP>.sql.gz`.
- Retention policy automatically prunes backups older than 7 days.

### B. Database Restoration
```bash
bash ./scripts/deploy/restore.sh /opt/ultron/backups/ultron_backup_<TIMESTAMP>.sql.gz
```

### C. Emergency Rollback
If a deployment fails or state corruption occurs:
```bash
bash ./scripts/deploy/rollback.sh
```
- Stops active container stack and restores stable container versions.

---

## 7. Health & Observability Endpoints

- **Liveness Probe**: `GET http://localhost:8000/health/live` (HTTP 200 OK `{ "status": "live" }`)
- **Readiness Probe**: `GET http://localhost:8000/health/ready` (HTTP 200 OK `{ "status": "ready", "database": "ok", "redis": "ok" }`)
- **Metrics Endpoint**: `GET http://localhost:8000/api/v1/metrics` (Prometheus formatted metrics)
