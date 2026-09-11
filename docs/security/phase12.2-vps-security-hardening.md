# PROJECT ULTRON — VPS SECURITY HARDENING PLAN

---

## 1. Operating System & Network Hardening

* **SSH Key-Only Auth**: Disable password SSH authentication (`PasswordAuthentication no`, `PermitRootLogin no` in `/etc/ssh/sshd_config`).
* **Uncomplicated Firewall (UFW)**: Allow ports `22` (SSH), `80` (HTTP), `443` (HTTPS) only.
* **Internal Service Binding**: MySQL (`3306`) and Redis (`6379`) exposed strictly to internal docker network (`expose` only, no `ports` binding to host IP).
* **Fail2Ban Protection**: Ban IP addresses exceeding 5 failed SSH attempts within 10 minutes.
* **Automatic Security Patching**: Enable `unattended-upgrades` on Ubuntu/Debian host.

---

## 2. Docker & Container Security

* **Non-Root Execution**: Backend and worker processes execute as `ultron:ultron` (UID 10000).
* **Memory & CPU Bounds**: Docker Compose resource limits configured (`memory: 1536M` backend, `memory: 1024M` worker, `memory: 1024M` mysql).
* **Production Secret Guard**: `settings.validate_production_secrets()` fails closed at container startup if default secrets or `DEBUG=True` are set.
* **Reverse Proxy Headers**: Nginx enforces HSTS (`max-age=31536000`), CSP, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`).
