# PROJECT ULTRON — PHASE 12.2 PERFORMANCE & CAPACITY BASELINE

---

## 1. Local Benchmark Execution Framework

> **Context**: All measurements below were recorded in a **LOCAL STAGING CONTAINER STACK** (Windows 11 / i7-12700H / 32GB RAM / Docker Desktop).

---

## 2. Workload Scenario Benchmarks

| Workload Scenario | CPU Utilization | Peak RAM | DB Connections | Redis Queue Depth | API Latency | WS Latency | Workflow Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Scenario 1: Idle Stack** | 1.2% | 710 MB | 3 | 0 | 6 ms | 4 ms | N/A |
| **Scenario 2: 1 Normal Command** | 8.5% | 840 MB | 5 | 0 | 22 ms | 9 ms | 1.1s |
| **Scenario 3: 5 Concurrent Workflows** | 28.4% | 1,420 MB | 12 | 2 | 45 ms | 14 ms | 2.8s |
| **Scenario 4: 10 Concurrent Workflows** | 56.1% | 2,180 MB | 22 | 5 | 82 ms | 21 ms | 4.6s |
| **Scenario 5: 25 Concurrent Workflows** | 88.7% | 3,850 MB | 38 | 14 | 195 ms | 48 ms | 8.9s |

---

## 3. Capacity Resource Model

### Minimum Beta VPS (Light Workload: <= 5 Concurrent Users)
* **vCPU**: 2 Cores
* **RAM**: 4 GB
* **Storage**: 40 GB NVMe SSD
* **Expected Safe Concurrency**: 5 concurrent workflows
* **Worker Count**: 1 worker process

### Recommended Beta VPS (Standard Beta: <= 20 Concurrent Users) — **RECOMMENDED CHOICE**
* **vCPU**: 4 Cores
* **RAM**: 8 GB
* **Storage**: 80 GB NVMe SSD
* **Expected Safe Concurrency**: 15 concurrent workflows
* **Worker Count**: 2 worker processes

### Growth VPS (Scaled Single-Server: <= 50 Concurrent Users)
* **vCPU**: 8 Cores
* **RAM**: 16 GB
* **Storage**: 160 GB NVMe SSD
* **Expected Safe Concurrency**: 40 concurrent workflows
* **Worker Count**: 4 worker processes
