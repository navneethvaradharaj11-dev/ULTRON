# Phase 5 Security & Controlled Computer Interaction Model

## Security Guarantees
1. **No Unrestricted Host Control**: ULTRON does NOT permit raw operating system execution, registry modifications, firewall tampering, or credential extraction.
2. **Confidence Thresholding**:
   - `confidence >= 0.85`: Action allowed automatically.
   - `0.60 <= confidence < 0.85`: Action requires confirmation/additional observation.
   - `confidence < 0.60`: Action denied (`LOW_CONFIDENCE`).
3. **Viewport Bounds Validation**: Coordinates outside the active viewport (`width` x `height`) are strictly rejected (`FORBIDDEN`).
4. **Approval Enforcement**: High-impact sensitive actions (sending messages, financial transactions, sensitive form submissions, data deletion, security setting changes, software installation, credential access) require backend user approval (`REQUIRES_APPROVAL`).
5. **Prompt Injection Isolation**: OCR text and visual summaries are wrapped inside `UNTRUSTED VISUAL DATA` isolation blocks and never executed as system instructions.
6. **Rate & Timeout Limits**: Server-side action limits (`MAX_COMPUTER_ACTIONS = 20`) and action timeouts (`COMPUTER_ACTION_TIMEOUT = 10.0s`).
7. **Session Ownership Verification**: Cross-user session access is strictly prohibited (`ACCESS_DENIED`).
