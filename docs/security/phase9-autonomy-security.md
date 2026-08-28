# Phase 9 Security Architecture — Autonomy Security & Risk Controls

## Principles
1. **User Authority**: Autonomy determines *WHEN* to act within pre-authorized permissions. It does *NOT* grant new permissions.
2. **Autonomy Level Governance**:
   - `LEVEL_0`: OBSERVE_ONLY
   - `LEVEL_1`: NOTIFY_ONLY
   - `LEVEL_2`: LOW_RISK_AUTONOMOUS_ACTION
   - `LEVEL_3`: APPROVAL_REQUIRED (Requires `ApprovalCoordinator` / human approval)
   - `LEVEL_4`: FORBIDDEN (Blocked)
3. **Multi-Tenant Isolation**: Mandatory `user_id` validation across database queries, REST endpoints, and WebSockets.
4. **Secret Protection**: `SecretDetector` sanitizes all titles and summaries before notification dispatch.
5. **Prompt Injection Boundary**: Untrusted content wrapped in `<untrusted_knowledge_source>` tags cannot alter autonomy policies.
