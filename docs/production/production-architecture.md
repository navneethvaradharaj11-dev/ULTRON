# ULTRON PRODUCTION ARCHITECTURE & OPERATIONS GUIDE

---

## 1. Top-Level Production Topology

```
USER MOBILE APP (Flutter)
       │
     HTTPS / WSS
       ▼
Nginx Reverse Proxy (SSL Termination, Rate Limiting, Security Headers)
       │
  ┌────┴───────────────────────────┐
  ▼                                ▼
FastAPI App Server (Port 8000)   Redis (Queue / Locks / Rate Limiting)
  │                                │
  ├────────────────────────────────┼─────────────────┐
  ▼                                ▼                 ▼
UltronCore & Multi-Agent DAG     Background Worker   MySQL Database (Port 3306)
  │ (Playwright / Sandbox)         (Knowledge / Jobs)
```

---

## 2. Infrastructure Components

* **API Application**: Containerized FastAPI Python 3.11 service executing as non-root user `ultron:ultron`.
* **Database Layer**: MySQL 8.0 with connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=1800`).
* **Caching & Queue**: Redis 7-Alpine for distributed locks (`lock:*`), worker task queues (`queue:default`), and sliding-window rate limiting.
* **Reverse Proxy**: Nginx 1.25 Alpine with SSL termination, WebSocket HTTP `Upgrade` header forwarding, HSTS, CSP, and connection limits.
* **Background Worker**: `BackgroundWorker` process handling asynchronous workflows, knowledge ingestion, retries, and Dead-Letter Queue (DLQ) routing.
