# Phase 11 Integration Security Specification

## 1. Secret Protection & Credential Encryption
- OAuth tokens, refresh tokens, and API keys are encrypted at rest using AES-256 / SHA-256 key derivation.
- Credentials are isolated per `user_id` tenant and never returned in API responses or agent logs.
- Secrets detected in payloads are automatically masked with `[REDACTED_SECRET]`.

## 2. External Prompt Injection Isolation
- All external data originating from GitHub issues, pull requests, email messages, calendar descriptions, or file payloads is wrapped in strict `<untrusted_data_source>` tags.
- LLM agents are explicitly instructed to process payload content as untrusted data without executing embedded instructions.

## 3. Human Approval Gates
- High-risk operations (`MERGE_PULL_REQUEST`, `SEND_EMAIL`, `DELETE_EMAIL`, `CANCEL_EVENT`) require explicit human approval before execution.
