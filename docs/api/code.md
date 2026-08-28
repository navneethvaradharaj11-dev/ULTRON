# Phase 4 REST API Reference — Code Intelligence & Sandbox

All endpoints require JWT Bearer Authentication (`Authorization: Bearer <token>`).

## Workspaces
- `POST /api/v1/code/workspaces` — Create new workspace.
- `GET /api/v1/code/workspaces` — List workspaces owned by current user.
- `GET /api/v1/code/workspaces/{id}` — Get workspace details and file list.

## Workspace Files
- `POST /api/v1/code/workspaces/{id}/files` — Create file in workspace.
- `GET /api/v1/code/workspaces/{id}/files` — List files in workspace.
- `PUT /api/v1/code/workspaces/{id}/files/{file_id}` — Update workspace file.
- `DELETE /api/v1/code/workspaces/{id}/files/{file_id}` — Delete file from workspace.

## Execution & Testing
- `POST /api/v1/code/execute` — Execute code inside isolated sandbox.
- `GET /api/v1/code/executions` — List user's code executions.
- `GET /api/v1/code/executions/{id}` — Get execution status, stdout, and stderr.
- `POST /api/v1/code/executions/{id}/cancel` — Cancel active execution and terminate sandbox processes.
- `POST /api/v1/code/test` — Run test suite inside isolated sandbox.
- `GET /api/v1/code/executions/{id}/artifacts` — List execution artifacts.
