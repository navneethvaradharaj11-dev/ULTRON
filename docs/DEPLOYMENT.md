# PROJECT ULTRON — Production Deployment Guide

This guide details how to deploy PROJECT ULTRON Phase 12.8 to a remote Linux VPS (DigitalOcean Droplet, Hetzner Cloud, AWS EC2, or Azure VM) using Docker Compose and `ultronctl.sh`.

---

## 1. System Requirements

| Resource | Minimum | Recommended Production |
| :--- | :--- | :--- |
| **OS** | Ubuntu 22.04 LTS / Debian 12 | Ubuntu 24.04 LTS |
| **vCPU** | 2 vCPU | 4 vCPU |
| **RAM** | 2 GB (with swap) | 4 GB - 8 GB |
| **Disk** | 25 GB NVMe SSD | 50 GB NVMe SSD |
| **Network** | Static Public IPv4 | Static IPv4 + IPv6 |
| **Firewall** | UFW / Cloud Security Groups | Ports 80, 443, 22 (SSH) open |

---

## 2. Pre-Deployment Setup on Remote VPS

### Step 1: Install Docker & Docker Compose
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl ufw git jq

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose plugin
sudo apt install -y docker-compose-plugin
docker compose version
```

### Step 2: Configure Host Firewall
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### Step 3: Clone Repository on Server
```bash
sudo mkdir -p /opt/ultron
sudo chown -R $USER:$USER /opt/ultron
git clone https://github.com/navneethvaradharaj11-dev/ULTRON.git /opt/ultron
cd /opt/ultron
```

---

## 3. Environment Configuration

Copy `.env.production.example` to `.env.production`:
```bash
cp .env.production.example .env.production
chmod 600 .env.production
```

Edit `.env.production` and configure mandatory production values:
```bash
# 1. Generate a secure 32+ byte random JWT secret
openssl rand -base64 32

# 2. Set database password
MYSQL_PASSWORD=your_super_strong_database_password_here

# 3. Set your production domain for CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# 4. Set AI provider credentials
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key_here
```

---

## 4. One-Click Deployment via `ultronctl.sh`

ULTRON includes the `ultronctl.sh` deployment state machine:

```bash
chmod +x scripts/ultronctl.sh scripts/deploy/*.sh

# Run preflight validation
./scripts/ultronctl.sh preflight

# Execute full 10-stage deployment
./scripts/ultronctl.sh deploy
```

The 10-stage deployment executes:
1. `PRECHECK`: Environment, permissions, and security policy validation.
2. `BACKUP`: Snapshot creation of existing database state.
3. `BUILD`: Docker multi-stage image build without caching.
4. `MIGRATE`: Idempotent database schema migration.
5. `DEPLOY`: Docker Compose service start in daemon mode.
6. `HEALTHCHECK`: Verification of liveness (`/health/live`) and readiness (`/health/ready`).
7. `HTTPS CHECK`: TLS security verification.
8. `WSS CHECK`: WebSocket bidirectional streaming probe.
9. `SMOKE TEST`: REST API and metrics exposition probe.
10. `READY`: Confirmation and service activation.

---

## 5. Setting Up Public HTTPS & WSS (Let's Encrypt)

If using Certbot for Let's Encrypt certificates:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d your-domain.com

# Link certificates to nginx volume
mkdir -p ./nginx/certs
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/certs/
```

---

## 6. Verification Commands

```bash
# Check container status
./scripts/ultronctl.sh status

# Query health probes
./scripts/ultronctl.sh health

# Tail service logs
./scripts/ultronctl.sh logs

# Run smoke test against custom endpoint
./scripts/ultronctl.sh smoke-test http://localhost:8000
```

---

## 7. Emergency Rollback & Recovery

If any deployment failure occurs:
```bash
# Rollback immediately to previous container state
./scripts/ultronctl.sh rollback

# Restore database from previous backup
./scripts/ultronctl.sh restore /opt/ultron/backups/backup_YYYYMMDD_HHMMSS.sql.gz
```
