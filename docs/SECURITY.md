# PROJECT ULTRON — Production Security Model & Audit Policy

This document outlines the security architecture, threat model, defenses, and 33-point red-team mitigation battery for PROJECT ULTRON Phase 12.8.

---

## 1. Core Security Principles

1. **Fail-Closed by Default**: Any unhandled condition, invalid token, failed parameter validation, or missing permission scope halts execution immediately.
2. **Multi-Tenant Isolation**: Every database query, memory retrieval, file sandbox path, and WebSocket session is strictly partitioned by authenticated `user_id`.
3. **Defense-in-Depth**:
   - Network layer (reverse proxy, TLS, rate limiting).
   - Application gateway layer (JWT verification, blacklist revocation, CORS).
   - Core engine layer (capability permission scopes, approval gates).
   - Execution layer (process limits, network isolation, filesystem sandbox chroot).

---

## 2. Authentication & Token Management

- **JWT Signing**: HS256 algorithm with minimum 32-byte secret key enforced in production.
- **Revocation & Blacklisting**: Token revocation managed via Redis with automatic in-memory fallback.
- **Token Invalidation**: Immediate invalidation on logout or password rotation.
- **Password Hashing**: Bcrypt / Argon2id with adaptive work factor.

---

## 3. Sandboxing & Process Isolation

- **Filesystem Chroot**: Sandbox runs inside dedicated per-session folders under `sandbox/`.
- **Path Traversal Shield**: Path resolution canonicalizes paths and validates that they reside strictly within the user's allocated sandbox directory. Path escapes (`../`, `C:\Windows`, `/etc/passwd`) are rejected with `PermissionDenied`.
- **System Call & Process Limits**: Strict limits on subprocess execution time (`CODE_EXECUTION_TIMEOUT`), maximum memory (`CODE_MAX_MEMORY_MB`), and total agent steps (`MAX_AGENT_STEPS`).
- **Network Jail**: Sandbox execution blocks outbound socket creation by default (`DENY_ALL`).

---

## 4. 33-Point Red-Team Attack Battery & Defense Matrix

| Attack ID | Threat Category | Attack Vector | Result | Mitigating Defense Mechanism |
| :---: | :--- | :--- | :---: | :--- |
| **01** | Auth / JWT | Forged Token Signature | `PASS` | `token_manager.decode_token` signature verification |
| **02** | Auth / JWT | Expired Token | `PASS` | `token_manager.decode_token` exp timestamp check |
| **03** | Auth / JWT | Revoked Token Reuse | `PASS` | `token_manager.is_token_revoked` Redis / memory blacklist |
| **04** | SSRF | Localhost Loopback Access | `PASS` | `BrowserSecurity.validate_url` loopback filter |
| **05** | SSRF | Private LAN IP Access | `PASS` | `BrowserSecurity.validate_url` private IP blocklist |
| **06** | SSRF | Cloud Metadata API Probe | `PASS` | `BrowserSecurity.validate_url` 169.254.169.254 filter |
| **07** | Browser | Scheme Escape (`file:///`) | `PASS` | `BrowserPolicy.validate_url` scheme whitelist (`http`/`https` only) |
| **08** | Browser | Script Injection (`javascript:`) | `PASS` | `BrowserPolicy.validate_url` blocked scheme filter |
| **09** | Sandbox | Path Traversal (`../../../`) | `PASS` | `SandboxFilesystem.resolve_path` root jail check |
| **10** | Sandbox | OS System Path Access | `PASS` | `SandboxFilesystem.resolve_path` canonicalization |
| **11** | Sandbox | Secret Configuration Read (`.env`) | `PASS` | `SandboxPolicy.evaluate_action` policy engine |
| **12** | Sandbox | Production Secret Read (`.env.prod`)| `PASS` | `SandboxPolicy.evaluate_action` policy engine |
| **13** | Prompt Inj. | Untrusted Prompt Hijack | `PASS` | `KnowledgeSecurity.wrap_untrusted_content` container |
| **14** | Secrets | API Key Exposure in Text | `PASS` | `SecretDetector.detect_secrets` pattern detector |
| **15** | Secrets | Secret Exposure in Agent Logs | `PASS` | `SecretDetector.sanitize_text` redaction scrubber |
| **16** | Autonomy | Destructive Level 4 Action | `PASS` | `AutonomyPolicyEngine.evaluate_policy` level 4 blocker |
| **17** | Computer | Cross-Tenant Computer Session | `PASS` | `ComputerSecurityValidator.validate_session_access` |
| **18** | Multi-Tenant | Cross-Tenant Knowledge Read | `PASS` | `KnowledgeEngine.query_knowledge` workspace filter |
| **19** | Resource | Agent Step Overflow Attack | `PASS` | `settings.MAX_AGENT_STEPS` hard limit |
| **20** | Resource | Infinite Loop Execution | `PASS` | `ProcessManager` timeout kill tree |
| **21** | Resource | Memory Exhaustion Attack | `PASS` | Resource limits configuration |
| **22** | SQLi | SQL Injection in Auth/API | `PASS` | SQLAlchemy parameterized statements |
| **23** | Password | Weak Password Hash Algorithm | `PASS` | Bcrypt / Argon2id enforcement |
| **24** | CORS | Wildcard CORS Header in Prod | `PASS` | `settings.validate_production_secrets()` blocker |
| **25** | Network | Unencrypted HTTP in Release | `PASS` | Flutter `ApiService` release build guard |
| **26** | Network | Insecure WS:// Scheme in Release | `PASS` | Flutter `WebSocketService` WSS protocol derivation |
| **27** | Autonomy | High-Risk Integration Write | `PASS` | `ScopeManager.requires_approval` gate |
| **28** | Computer | Viewport Out-of-Bounds Click | `PASS` | `ComputerSecurityValidator` coordinate bounds check |
| **29** | Computer | Low Confidence Action Execution | `PASS` | Vision threshold validation |
| **30** | Browser | Form Credential Auto-Fill Leak | `PASS` | `BrowserSecurity.detect_login_form` requirement |
| **31** | Artifact | Path Traversal File Export | `PASS` | Artifact filepath MD5 checksum hashing |
| **32** | Failure | Log Exception Secret Leak | `PASS` | `FailureManager.classify_failure` message scrubber |
| **33** | System | Cooldown Window Bypass | `PASS` | `CooldownManager` timestamp registry |

---

## 5. Emergency Shutdown Circuit Breaker

ULTRON includes a built-in emergency control switch:
- **API Endpoint**: `POST /api/v1/ultron/emergency-shutdown`
- **Behavior**:
  - Immediately toggles `EMERGENCY_SHUTDOWN_ACTIVE = True`.
  - Halts autonomous background trigger evaluation.
  - Pauses dispatch of new workflow DAGs and connector writes.
  - Retains all persistent user data, knowledge bases, and checkpoints intact.
  - Can be queried via `GET /api/v1/health`.
