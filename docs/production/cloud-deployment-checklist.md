# PROJECT ULTRON — CLOUD DEPLOYMENT CHECKLIST & PACKAGE

---

## 1. Cloud Provisioning Checklist

- [ ] **VM Provisioning**: AWS EC2 / GCP Compute Engine / DigitalOcean Droplet (2+ vCPU, 4GB+ RAM, 20GB+ SSD).
- [ ] **Public Networking**: Static Public IP address assigned to host instance.
- [ ] **DNS Record**: `A` record configured pointing domain (e.g., `api.ultron.ai`) to Public IP.
- [ ] **TLS Certificate**: Obtain SSL certificate via Let's Encrypt / Certbot (`/etc/ssl/certs/ultron.crt`).
- [ ] **Firewall Inbound Ports**: Open `80` (HTTP) and `443` (HTTPS) to public; keep `3306`, `6379`, `8000` internal.

---

## 2. Container Deployment Runbook

```bash
# 1. Clone repository to server
git clone https://github.com/org/ultron.git /opt/ultron
cd /opt/ultron

# 2. Configure production secrets
cp .env.production.example .env
nano .env

# Mandatory Env Overrides:
# ENVIRONMENT=production
# DEBUG=False
# JWT_SECRET=<generated_secure_32_byte_secret>
# MYSQL_PASSWORD=<strong_mysql_password>

# 3. Launch container stack
docker-compose up --build -d

# 4. Verify liveness & readiness
curl -f http://localhost/health/live
curl -f http://localhost/health/ready
```

---

## 3. Mobile Build Release Configuration

```bash
cd frontend/flutter_app
flutter build apk --release \
  --dart-define=API_BASE_URL=https://api.ultron.ai/api/v1 \
  --dart-define=WS_BASE_URL=wss://api.ultron.ai/ws
```
