# PROJECT ULTRON — PHASE 12.7 PRODUCTION LAUNCH RUNBOOK

---

## 1. Operator Quick Reference & System Version

- **Application Version**: `12.7.0`
- **Target OS**: Ubuntu 22.04 LTS / 24.04 LTS
- **Primary CLI Utility**: `./scripts/ultronctl.sh`

---

## 2. Zero-to-Live Production Launch Protocol

Follow these steps when launching ULTRON on a newly provisioned Ubuntu VPS instance:

```bash
# Step 1: Connect to VPS host
ssh root@<VPS_PUBLIC_IPV4>

# Step 2: Clone repository to target directory
git clone https://github.com/ultron-ai/ULTRON.git /opt/ultron
cd /opt/ultron

# Step 3: Configure production secrets
cp .env.production.example /opt/ultron/.env.production
nano /opt/ultron/.env.production # Populate secure 32+ byte JWT_SECRET and MYSQL_PASSWORD

# Step 4: Run Pre-Flight Validation (Must return PASS)
./scripts/ultronctl.sh preflight

# Step 5: Execute Zero-to-Live Deployment State Machine
./scripts/ultronctl.sh deploy

# Step 6: Provision Let's Encrypt TLS Certificate (after DNS A record propagation)
bash ./scripts/deploy/setup_https.sh <DOMAIN_NAME> admin@<DOMAIN_NAME>

# Step 7: Verify Smoke Test Suite
./scripts/ultronctl.sh smoke-test https://<DOMAIN_NAME>
```

---

## 3. Operations & System Monitoring

- **Check System Health Probes**:
  ```bash
  ./scripts/ultronctl.sh health
  ```
- **Inspect Container Stack & Status**:
  ```bash
  ./scripts/ultronctl.sh status
  ```
- **Stream Live Logs**:
  ```bash
  ./scripts/ultronctl.sh logs
  ```

---

## 4. Disaster Recovery & Emergency Procedures

### A. Emergency Stack Rollback
If a deployment fails health validation:
```bash
./scripts/ultronctl.sh rollback
```

### B. Database Restoration
To restore database state from a backup file:
```bash
./scripts/ultronctl.sh restore /opt/ultron/backups/ultron_backup_<TIMESTAMP>.sql.gz
```

### C. Emergency Autonomy Shutdown
To immediately halt background autonomy triggers and external integrations without destroying application state:
```bash
curl -X POST https://<DOMAIN_NAME>/api/v1/ultron/emergency-shutdown \
  -H "Authorization: Bearer <ADMIN_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Operational safety inspection"}'
```
