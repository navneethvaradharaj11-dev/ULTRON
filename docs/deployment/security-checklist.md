# PROJECT ULTRON — Production Security Verification Checklist

- [x] **Authentication**: Short-lived JWT tokens, password hashing via bcrypt, token revocation tracker.
- [x] **Multi-Tenancy**: Mandatory `user_id` scoping across database models and API repositories.
- [x] **SSRF Protection**: Explicit loopback (`127.0.0.1`, `localhost`), metadata IP (`169.254.169.254`), and private RFC 1918 IP blocking in `BrowserSecurity`.
- [x] **Sandbox Jail**: Fail-closed process sandbox with path traversal protection, forbidden root execution, and system environment secret stripping.
- [x] **Perception Bounds**: Visual grounding confidence thresholding (`>= 0.85` allowed, `0.60–0.84` approval, `< 0.60` rejected).
- [x] **Prompt Injection Isolation**: External webpage, OCR, document, and memory text strictly wrapped in `<untrusted_data_source>` tags.
- [x] **Secret Redaction**: Secret patterns automatically masked before logging, persistence, or client response formatting.
- [x] **Human Approval Gates**: Sensitive actions (payments, file deletions, dangerous shell execution) require explicit user approval.
