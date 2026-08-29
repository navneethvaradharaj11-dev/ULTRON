# PROJECT ULTRON — SINGLE-VPS & FUTURE SCALING ARCHITECTURE

---

## 1. Single-VPS Initial Beta Topology

```text
INTERNET (HTTPS / WSS)
   │
   ▼
[Port 80/443] Nginx Reverse Proxy (SSL Termination, HSTS, Security Headers)
   │
   ├──────► [Port 8000] FastAPI Backend (UltronCore, Intent Engine, REST/WS)
   │           │
   │           ├──► Redis 7 (Queues, Locks, Rate Limiting)
   │           ├──► MySQL 8.0 (Persistent State, Workflows, Audit)
   │           ├──► Playwright Chromium (Browser Sandbox Sessions)
   │           └──► Subprocess Jail (Python Code Sandbox)
   │
   └──────► Background Worker Process (Knowledge Ingestion, Retries, DLQ)
```

---

## 2. Future Migration Path (Multi-Node Cloud Architecture)

### Phase 1: Decoupled Services
```text
FastAPI API Server (VPS 1) ──► Managed MySQL (Database Service)
Worker Server (VPS 2)       ──► Managed Redis (Cluster Service)
                            ──► AWS S3 / GCS (Object Storage)
```

### Phase 2: Load-Balanced Scale-Out
```text
              Cloud Load Balancer
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
   API Server Node #1        API Server Node #2
          │                         │
          └────────────┬────────────┘
                       ▼
                 Managed Redis
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
  Worker Node 1   Worker Node 2   Worker Node 3
       │               │               │
       └───────────────┼───────────────┘
                       ▼
               Managed MySQL 8.0
```
