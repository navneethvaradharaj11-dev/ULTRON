# ULTRON PRODUCTION DEPLOYMENT GUIDE

---

## 1. Prerequisites

* Docker Engine 24.0+ & Docker Compose v2.x
* SSL/TLS Certificate & Private Key (placed in `/etc/ssl/certs/ultron.crt` and `/etc/ssl/certs/ultron.key`)
* Domain name configured to point to proxy IP

---

## 2. Environment Setup

Copy `.env.example` to `.env` and set mandatory production values:

```env
ENVIRONMENT=production
DEBUG=False
JWT_SECRET=<32-byte-random-secure-secret>
MYSQL_PASSWORD=<strong-database-password>
```

---

## 3. Launching Container Stack

```bash
docker-compose up --build -d
```

Verify container status:

```bash
docker-compose ps
```

---

## 4. Verification

* Check backend liveness: `curl http://localhost/health/live`
* Check backend readiness: `curl http://localhost/health/ready`
* Check metrics: `curl http://localhost/metrics`
