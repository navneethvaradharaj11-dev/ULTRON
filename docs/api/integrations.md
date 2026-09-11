# Phase 11 Integration REST API Reference

## Endpoints

### 1. List Integrations
`GET /api/v1/integrations`
Returns registered integrations, health status, and user connection status.

### 2. Connect Integration
`POST /api/v1/integrations/{id}/connect`
Connects an integration for the authenticated user.

### 3. Disconnect Integration
`POST /api/v1/integrations/{id}/disconnect`
Disconnects an integration.

### 4. Execute Integration Operation
`POST /api/v1/integrations/execute`
Executes an operation through the Integration Manager pipeline.
Payload:
```json
{
  "integration_id": "github",
  "operation_id": "get_repository",
  "parameters": { "owner": "navneethvaradharaj11-dev", "repo": "ULTRON" }
}
```

### 5. Audit Log Events
`GET /api/v1/integrations/events`
Returns integration execution audit logs for the authenticated user.
