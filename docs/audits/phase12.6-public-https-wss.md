# PROJECT ULTRON — PHASE 12.6 PUBLIC HTTPS & WSS AUDIT

---

## 1. Domain & Network Protocol Matrix

```text
DOMAIN:   PENDING
DNS:      PENDING
HTTPS:    PENDING
WSS:      PENDING
```

---

## 2. Protocol Configuration Verification

### A. HTTP -> HTTPS Redirect & TLS Security
- **Nginx Config (`nginx/nginx.conf`)**:
  - Port 80 server block configured to issue HTTP 301 permanent redirect to `https://$host$request_uri`.
  - SSL/TLS protocols restricted to TLSv1.2 and TLSv1.3.
  - Ciphers set to modern high-security suites.
  - HSTS (`Strict-Transport-Security`) header configured with `max-age=31536000`.
- **Let's Encrypt Provisioning (`scripts/deploy/setup_https.sh`)**:
  - Automated Certbot execution with `--nginx` plugin and `--non-interactive` flag.
  - Auto-renewal cron dry-run test (`certbot renew --dry-run`).

### B. WebSocket / WSS Reverse Proxy
- **Endpoint 1**: `wss://DOMAIN/ws/chat/{id}`
  - Proxy directives set `Upgrade $http_upgrade`, `Connection "Upgrade"`, `Host $host`.
  - Proxy timeout set to 86400s (24h) for persistent mobile agentic chat streams.
- **Endpoint 2**: `wss://DOMAIN/ws/stream/{workflow_id}`
  - Event streaming channel for real-time autonomy telemetry and agent tool executions.
  - Authentication checked during initial connection handshake via JWT query token or Authorization header.

---

## 3. Public Verification Blocker

Public TLS certificate generation via ACME/Let's Encrypt requires:
1. A valid public domain name pointing to the VPS public IPv4 via DNS `A` record.
2. Port 80 accessible externally for HTTP-01 ACME challenge resolution.

Because no public domain or VPS host is allocated yet, TLS certificate issuance and external public WSS verification remain in **PENDING** state.

---

## 4. Final Verdict

**VERDICT**: **PUBLIC HTTPS / WSS PENDING DOMAIN ALLOCATION**
