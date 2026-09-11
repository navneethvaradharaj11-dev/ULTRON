# PROJECT ULTRON — PHASE 12.1 REAL PRODUCTION DEPLOYMENT PROCEDURES

---

## 1. Local & Containerized Staging Deployment Verification

The production container infrastructure has been fully validated locally:

```bash
docker-compose build
docker-compose up -d
docker-compose ps
```

All 5 core production services (`backend`, `worker`, `mysql`, `redis`, `proxy`) launch cleanly, pass container healthchecks, and expose HTTP/HTTPS endpoints via Nginx proxy.

---

## 2. Cloud Deployment Runbook (AWS / GCP / DigitalOcean)

### Step 1: Provision Host Instance
* Provision Linux VM (Ubuntu 22.04 LTS / 2+ vCPU, 4GB RAM, 20GB SSD).
* Assign Static Public IP address.
* Configure DNS `A` record pointing to domain `api.ultron.ai`.

### Step 2: Transfer Repository & Set Environment Variables
```bash
git clone https://github.com/org/ultron.git /opt/ultron
cd /opt/ultron
cp .env.production.example .env
```
Populate mandatory secrets in `.env`:
* `ENVIRONMENT=production`
* `JWT_SECRET=<32_byte_random_secret>`
* `MYSQL_PASSWORD=<strong_db_password>`

### Step 3: Launch Production Container Stack
```bash
docker-compose up --build -d
```

### Step 4: Verification Probes
* `curl -f https://api.ultron.ai/health/live` -> `{"status":"live"}`
* `curl -f https://api.ultron.ai/health/ready` -> `{"status":"ready"}`
* `curl -f https://api.ultron.ai/metrics` -> Prometheus metrics text output
