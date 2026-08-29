# PROJECT ULTRON — VPS SECURITY HARDENING SPECIFICATION

---

## 1. Network & Firewall Hardening

* **Allowed Public Inbound Ports**: `80` (HTTP), `443` (HTTPS), `22` (SSH).
* **Blocked Internal Ports**: `3306` (MySQL), `6379` (Redis), `8000` (FastAPI), `9222` (Playwright Debug).
* **Fail-Closed Configuration**: Missing secrets, weak JWT keys, or active `DEBUG=True` in production cause immediate container exit.

---

## 2. Security Boundaries Matrix

| Boundary | Control Mechanism | Status |
| :--- | :--- | :---: |
| **Tenant Isolation** | `user_id` context propagation & DB index filtering | **ACTIVE** |
| **SSRF Protection** | Private IP blocklists & DNS resolution validation | **ACTIVE** |
| **Prompt Injection** | Untrusted input wrapping & instruction isolation | **ACTIVE** |
| **Sandbox Jail** | Isolated workspace directory & path traversal blocking | **ACTIVE** |
| **Approval Gates** | Server-authoritative Level 3 approval verification | **ACTIVE** |
