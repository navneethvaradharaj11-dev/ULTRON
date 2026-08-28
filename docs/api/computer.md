# Phase 5 API: Controlled Computer Interaction

## Base Endpoint
`/api/v1/computer`

## Endpoints

### 1. Create Computer Session
- **URL**: `POST /api/v1/computer/sessions`
- **Request Body**:
  ```json
  {
    "execution_id": "exec_123",
    "viewport_width": 1280,
    "viewport_height": 800
  }
  ```

### 2. Execute Controlled Computer Action
- **URL**: `POST /api/v1/computer/sessions/{session_id}/actions`
- **Request Body**:
  ```json
  {
    "action_type": "CLICK",
    "target": {"label": "Submit Form"},
    "parameters": {"x": 100, "y": 200},
    "confidence": 0.95
  }
  ```

### 3. Approve / Reject Sensitive Action
- **URL**: `POST /api/v1/computer/actions/approve`
- **URL**: `POST /api/v1/computer/actions/reject`
- **Request Body**:
  ```json
  {
    "action_id": "act_789",
    "session_id": "sess_456"
  }
  ```
