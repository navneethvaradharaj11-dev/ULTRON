# PROJECT ULTRON — Production Deployment Guide

## Overview
This document provides production deployment instructions for running the **PROJECT ULTRON Personal Agent Operating System** backend, MySQL database, Playwright Chromium headless engine, and Flutter cross-platform mobile client.

---

## 1. System Requirements
- **OS**: Linux (Ubuntu 22.04 LTS recommended) or Windows Server 2022
- **Python**: Python 3.10+
- **Database**: MySQL Server 8.0+
- **Browser Runtime**: Node.js 18+ and Playwright Chromium 1.62+
- **Reverse Proxy**: NGINX / Caddy with HTTPS & WSS support

---

## 2. Infrastructure Setup & Environment
```bash
# 1. Clone repository
git clone https://github.com/navneethvaradharaj11-dev/ULTRON.git /opt/ultron
cd /opt/ultron

# 2. Virtual Environment Setup
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium

# 3. Environment Configuration
cp .env.example .env
```

---

## 3. Database Initialization & Migrations
```bash
# Run schema migrations
python -m backend.app.main
```

---

## 4. Production Service Management (Systemd)
```ini
[Unit]
Description=PROJECT ULTRON Agentic AI Operating System API
After=network.target mysql.service

[Service]
User=ultron
WorkingDirectory=/opt/ultron
ExecStart=/opt/ultron/backend/.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```
