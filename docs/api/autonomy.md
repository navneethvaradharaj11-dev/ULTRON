# Phase 9 Autonomy REST API Specifications

`Base Path: /api/v1/autonomy`

### Endpoints
- `POST /rules` — Create a new autonomy rule.
- `GET /rules` — List autonomy rules for user.
- `GET /rules/{id}` — Get rule detail.
- `POST /rules/{id}/enable` — Enable rule.
- `POST /rules/{id}/disable` — Disable rule.
- `DELETE /rules/{id}` — Delete rule.
- `POST /rules/{id}/test` — Manually trigger test event.
- `GET /events` — List audit event history.
- `GET /notifications` — List notifications.
- `POST /notifications/{id}/read` — Toggle notification read state.
