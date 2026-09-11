# PROJECT ULTRON — PHASE 12.2 RESOURCE & ARCHITECTURE AUDIT

---

## 1. Executive Summary

This **Phase 12.2 Resource & Architecture Audit** evaluates every process, worker thread, subprocess, database connection, and storage volume in **PROJECT ULTRON** to establish precise resource consumption footprints prior to cloud deployment.

---

## 2. Process Resource Consumption Matrix

| Process / Component | Execution Context | CPU Profile | Memory Baseline (RAM) | Storage Footprint | Connection Bounds |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **FastAPI Backend** | Python 3.11 Container | Low–Moderate | ~180 MB – 350 MB | Temp scratch / logs | 10 DB / 10 Redis |
| **Background Worker** | Python Subprocess | Moderate | ~120 MB – 250 MB | Queue log state | 5 DB / 5 Redis |
| **MySQL 8.0 Engine** | MySQL Container | Low–Moderate | ~350 MB – 600 MB | `/var/lib/mysql` volume | Max 50 conns |
| **Redis 7 In-Memory** | Redis Container | Low | ~30 MB – 80 MB | AOF / RDB volume | Max 100 conns |
| **Nginx Proxy** | C Alpine Container | Low | ~15 MB – 45 MB | Access/Error logs | 1024 workers |
| **Playwright Chromium** | Node/Browser Subprocess | High Spike | ~250 MB – 500 MB per page | `/sandbox/downloads` | 1 per task |
| **Python Sandbox Jail** | Isolated Subprocess | Moderate Spike | ~80 MB – 200 MB per exec | Scratch temp files | 1 per task |

---

## 3. Resource Pressure Drivers

1. **Chromium Headless Sessions**: Peak RAM consumer (spikes by ~350MB per concurrent browser tab).
2. **MySQL InnoDB Buffer Pool**: Default allocation consumes ~400MB RAM baseline.
3. **Sandbox Python Executions**: Subprocess creation causes temporary CPU utilization spikes (~15-25% CPU core per script).
