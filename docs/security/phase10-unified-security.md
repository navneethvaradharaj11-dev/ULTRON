# Phase 10 Security Architecture — Unified Security Gate & Risk Governance

## Principles
1. **Single Security Gate**: `UnifiedSecurityGate` enforces authentication, multi-tenant `user_id` isolation, capability permission limits, risk evaluation, and human approval gates across all 10 phases.
2. **Resource Bounding**: `ResourceBudgetTracker` limits max tool calls, browser steps, runtime duration, and sandbox memory per workflow.
3. **Secret Redaction**: `SecretDetector` masks API keys, passwords, connection strings, and tokens before persistence or client streaming.
4. **Prompt Injection Boundary**: External text content is strictly encapsulated in `<untrusted_knowledge_source>` tags to prevent policy override.
