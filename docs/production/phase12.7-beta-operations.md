# PROJECT ULTRON — PHASE 12.7 BETA OPERATIONS MANUAL

---

## 1. Executive Summary

This document specifies the operational policies, safety boundaries, rate limits, and autonomy controls governing beta users on the production ULTRON platform.

---

## 2. Beta User Safety Matrix

| Safety Boundary | Policy & Limit | Control Mechanism | Status |
| :--- | :--- | :--- | :--- |
| **Tenant Isolation** | Strict user-level data separation | SQLAlchemy `user_id` query scoping | ACTIVE |
| **Rate Limiting** | 60 requests / minute per IP/user | `ServerRateLimiterMiddleware` | ACTIVE |
| **Workflow Step Limits** | Max 10 agent steps per workflow | `MAX_AGENT_STEPS=10` in `settings` | ACTIVE |
| **Resource Quotas** | Max 512MB RAM, 10s CPU time per code task | Sandbox process resource limits | ACTIVE |
| **Autonomy Defaults** | Level 3 Approval required for external writes | `AutonomyPolicyManager` | ACTIVE |
| **Audit Logging** | Complete activity timeline recorded | `UltronRepository.record_activity` | ACTIVE |
| **User Feedback** | API endpoint for user reports | `POST /api/v1/feedback` | ACTIVE |
| **Emergency Disable** | Operator panic button endpoint | `POST /api/v1/ultron/emergency-shutdown` | ACTIVE |

---

## 3. Feedback & Telemetry Reporting

Beta users submit feedback via the Flutter Mobile App or Web interface:
- **Endpoint**: `POST /api/v1/feedback`
- **Payload**: `{ "category": "bug" | "feature" | "general", "message": "...", "workflow_id": "..." }`
- **Storage**: Persisted to MySQL `user_feedback` table.

---

## 4. Emergency Disable Mechanism

If abnormal activity or unexpected behavior is detected during beta testing:
1. Operator invokes `POST /api/v1/ultron/emergency-shutdown`.
2. All background autonomy triggers and integration webhooks halt immediately.
3. User workspace files and database state remain completely safe and uncorrupted.
