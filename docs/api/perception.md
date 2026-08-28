# Phase 5 API: Perception Engine

## Base Endpoint
`POST /api/v1/perception`

## Endpoints

### 1. Perceive UI State
- **URL**: `POST /api/v1/perception/perceive`
- **Headers**: `Authorization: Bearer <JWT>`
- **Request Body**:
  ```json
  {
    "execution_id": "exec_123",
    "dom_elements": [
      {
        "id": "btn_1",
        "tag": "button",
        "text": "Submit Form",
        "rect": {"x": 100, "y": 200, "width": 120, "height": 40}
      }
    ]
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "sess_456",
    "execution_id": "exec_123",
    "elements": [...],
    "total_elements": 1,
    "confidence": 0.95,
    "ocr_text": "Submit Form"
  }
  ```

### 2. Ground Instruction to Target
- **URL**: `POST /api/v1/perception/ground`
- **Headers**: `Authorization: Bearer <JWT>`
- **Request Body**:
  ```json
  {
    "instruction": "Click Submit Form button",
    "perception_data": { ... }
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "target": {
      "element_id": "btn_1",
      "description": "Submit Form",
      "bounding_box": {"x": 100, "y": 200, "width": 120, "height": 40},
      "confidence": 0.95
    }
  }
  ```
