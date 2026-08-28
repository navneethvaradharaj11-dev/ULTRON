# Memory Security & Secret Protection Model

## Secret Persistence Prevention
Before persistence, memory strings are processed through `SecretDetector`:
- API Keys & Auth Tokens (`sk_live_...`, `api_key: ...`)
- JWT Tokens
- Private Keys (RSA/EC PEM)
- Password credentials & database connection URLs
- Session cookies

Detected secrets are either rejected or sanitized with `[REDACTED_...]` placeholders.

## Prompt Injection Defense
Retrieved memories injected into model prompts are wrapped in:
`<untrusted_memory_data type="..." confidence="...">`
with explicit system instructions that memory text is untrusted user DATA.
