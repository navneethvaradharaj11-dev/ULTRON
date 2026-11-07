# Phase 3.1: WSL2 Mirrored Networking Test & Rollback Report

**Validation Date:** 2026-09-26  
**Host Environment:** Windows 11 Build 26200 + WSL 2.7.10.0 + Ubuntu 22.04 LTS  
**Target Approach Tested:** Approach 1 (WSL2 Mirrored Networking `networkingMode=mirrored`)  
**Rollback Triggered:** **YES** (Per Step 11 Rollback Condition)  
**Current System State:** Restored to safe, operational NAT baseline with 5/5 ULTRON containers healthy  

---

### A. PRE-CHECK
* **Status:** **PASS**
* **Prior Baseline Recorded:**
  - `~/.wslconfig`: `[wsl2] memory=6GB`
  - Active WSL2 Mode: Default NAT mode (`eth0: 172.26.79.85/20`)
  - Running Containers: 5/5 operational (`ultron_backend`, `ultron_worker`, `ultron_mysql`, `ultron_redis`, `ultron_proxy`)
  - Windows Listening Ports: `127.0.0.1:8000` (forwarded via WSL localhost forwarding service)
  - Backup Created: `C:\Users\Navneeth V\.wslconfig.bak` successfully saved.

---

### B. CONFIGURATION CHANGE
* **Status:** **PASS**
* Configuration applied to `C:\Users\Navneeth V\.wslconfig`:
  ```ini
  [wsl2]
  memory=6GB
  networkingMode=mirrored
  ```

---

### C. WSL STATUS UNDER MIRRORED MODE
* **Status:** **FAIL (Hyper-V Network Failure)**
* **Telemetry Error Output:**
  ```text
  wsl: An internal error occurred.
  Error code: CreateInstance/CreateVm/ConfigureNetworking/0x8007054f
  wsl: Failed to configure network (networkingMode Mirrored), falling back to networkingMode None.
  ```
* **Analysis:** On this Windows 11 Home Single Language build, WSL2's mirrored networking driver encountered Hyper-V virtual switch error `0x8007054f`. WSL fell back to `networkingMode None`, eliminating all external network adapters (`eth0` disappeared; only local loopback remained), severing container access from the host.

---

### D. DOCKER STATUS
* **Status:** **PASS (Post-Rollback)**
* **During Mirrored Mode:** Severed from Windows host due to network failure.
* **Post-Rollback (Restored NAT Mode):** Docker service active and healthy (`ServerVersion: 29.8.1`, `ContainersRunning: 5`).

---

### E. LOCAL HEALTH TEST
* **Status:** **PASS**
* **WSL Localhost (`http://localhost:8000/health`):** `HTTP/1.1 200 OK`
* **Windows Host Access (`http://172.26.79.85:8000/health`):** `HTTP/1.1 200 OK`
* **Payload Verification:**
  ```json
  {"status":"healthy","system":"ULTRON Agentic AI Operating System","version":"12.0.0","database":{"engine":"mysql","status":"healthy"},"ai_provider":{"name":"mock","model":"gemini-2.5-flash"},"registered_tools_count":30}
  ```

---

### F. TAILSCALE HEALTH
* **Status:** **WARNING (Bridging Required)**
* **Tailscale Client:** Connected and healthy on Windows host (`100.69.161.16`).
* **Direct Access on 100.69.161.16:8000:** Connection refused under standard NAT mode because Windows terminates incoming Tailnet packets on the virtual adapter without routing them to WSL2's internal virtual IP (`172.26.79.85`).
* **Conclusion:** `networkingMode=mirrored` is incompatible with the current Windows 11 Home Hyper-V network configuration. The standard and robust solution is Windows `netsh interface portproxy` or connecting Tailscale inside WSL.

---

### G. PORT / BINDING AUDIT
* **Status:** **PASS**
* Physical LAN / Wi-Fi exposure: **ZERO**
* External Router Forwarding: **ZERO**
* Active Binding: Port `8000` is bound to WSL2's internal virtual adapter (`172.26.79.85`), accessible by Windows host only.

---

### H. MYSQL ISOLATION
* **Status:** **PASS**
* Configured as `expose: ["3306"]` in `docker-compose.yml`.
* Port 3306 tested on `127.0.0.1` and `100.69.161.16` $\rightarrow$ **CLOSED / ISOLATED**.
* Database is accessible exclusively inside the Docker bridge network.

---

### I. REDIS ISOLATION
* **Status:** **PASS**
* Configured as `expose: ["6379"]` in `docker-compose.yml`.
* Port 6379 tested on `127.0.0.1` and `100.69.161.16` $\rightarrow$ **CLOSED / ISOLATED**.
* Cache is accessible exclusively inside the Docker bridge network.

---

### J. FIREWALL STATUS
* **Status:** **PASS**
* Windows Firewall remains fully active across Domain, Private, and Public profiles.
* No blanket Hyper-V inbound allow rules (`Set-NetFirewallHyperVVMSetting -DefaultInboundAction Allow`) were created.
* System security posture remains fail-closed.

---

### K. RESOURCE USAGE
* **Status:** **PASS**
* **WSL2 System Memory:** Enforced ceiling 6 GB; currently ~950 MB used (~5.0 GB available).
* **Docker Memory Footprint:** ~560 MB total for all 5 containers combined.
* **Disk Usage:** 12 GB used out of 1007 GB virtual disk.

---

### L. SECURITY
* **Status:** **PASS**
* Zero plaintext secrets exposed or logged.
* `.env` remains gitignored.
* Database and cache remain non-published.

---

### M. ₹0 COST
* **Status:** **PASS**
* Total cost: **₹0.00**. No paid tools, VPS, or cloud resources used.

---

### N. ROLLBACK STATUS
* **Status:** **PASS (Fully Executed & Verified)**
* Per Step 11 instructions, upon detecting `0x8007054f`:
  1. `~/.wslconfig` was restored from `~/.wslconfig.bak` (`[wsl2] memory=6GB`).
  2. `wsl --shutdown` was executed.
  3. WSL2 restarted cleanly in default NAT mode (`eth0: 172.26.79.85/20`).
  4. Docker daemon and ULTRON container stack were restored and verified healthy.

---

### O. FINAL VERDICT
* **Verdict:** **PASS (Safe Rollback & Working Baseline Confirmed)**
* **Key Finding:** Approach 1 (`networkingMode=mirrored`) triggers Hyper-V network initialization error `0x8007054f` on this Windows Home machine and cannot be used.
* **Next Recommendation:** To bridge Tailscale (`100.69.161.16:8000`) to ULTRON (`172.26.79.85:8000`) without compromising security, we should evaluate Approach 2 (specific Windows `netsh interface portproxy` mapping) or running Tailscale client inside WSL2.
