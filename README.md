# PROJECT ULTRON — Agentic AI Operating System

An advanced, production-grade **Agentic AI Operating System** featuring a DAG-based Task Graph execution engine, observation loops (`PLAN` → `ACT` → `OBSERVE` → `EVALUATE`), structured multi-agent orchestration, backend-validated approval security, process crash recovery, deterministic evaluation harness, per-agent performance metrics, real-time WebSocket event streaming, and a Flutter cross-platform UI.

---

## 🌟 Key Highlights & Capabilities

- **DAG Task Graph Engine (`TaskGraph` / `TaskNode`)**: Dynamically resolves sub-task dependencies using topological sorting and Kahn's algorithm cycle validation.
- **Specialized Multi-Agent Swarm**:
  - **Commander**: Intent recognition & high-level strategy coordination.
  - **Planner**: Generates structured DAG plans with strict Pydantic schema validation.
  - **Researcher**: Information gathering & web research synthesis.
  - **Coder**: Code generation, syntax analysis, and tool execution.
  - **Reviewer**: Evaluates task output quality, returning structured confidence scores, issue lists, and approval/rejection decisions.
- **Agentic Reliability & Execution Persistence (Phase 2.5)**:
  - **Idempotency Key Deduplication**: Prevents duplicate executions on client retries via `idempotency_key`.
  - **Process Crash Recovery**: `rebuild_graph_from_db()` reconstructs task graphs after process interruptions, resetting orphaned `RUNNING` tasks to `PENDING` while preserving `COMPLETED` tasks.
  - **State Machine Guards**: Formal state transitions for `Execution` and `ExecutionTask` prevent illegal status jumps.
  - **Event Consistency Inspector**: Automated timeline validation verifying start, completion, and task matching integrity.
- **Evaluation Harness & Metrics**:
  - **Deterministic Dataset (`eval_dataset.json`)**: Test scenarios covering calculations, multi-step research, code generation, and complex 4-step E2E workflows.
  - **E2E Eval Runner (`test_eval_harness.py`)**: Runs goals through the live stack with 100% aggregate pass rate verification.
  - **Per-Agent Metrics (`execution_metrics`)**: Tracks duration, success/failure rate, retries, and review confidence per agent.
- **Interactive Flutter UI**:
  - **Execution History & Tabbed Goal View**: Live progress monitoring, goal submission, inline Cancel/Resume actions.
  - **Task Graph & Event Timeline**: Detailed visual task status cards and chronological event sequence timeline with payload previews and consistency badge.
  - **Agent Analytics Tab**: Visual linear progress bars tracking success rate and average execution time per agent.
- **Security & Sandboxing**: Server-side tool approval prompts, strict filesystem sandboxing, and JWT-authenticated WebSockets.

---

## 🏗️ Architecture & System Topology

```
                       ┌──────────────────────────────────┐
                       │     FLUTTER CROSS-PLATFORM UI    │
                       │ (Executions / History / Detail)  │
                       └────────────────┬─────────────────┘
                                        │
                                   REST / WS
                                        │
                       ┌────────────────▼─────────────────┐
                       │       FASTAPI BACKEND API        │
                       │  (Executions, Chat, Auth, Tools) │
                       └────────────────┬─────────────────┘
                                        │
                       ┌────────────────▼─────────────────┐
                       │          ULTRON CORE             │
                       │ (Intent Router & Context Builder)│
                       └────────────────┬─────────────────┘
                                        │
         ┌──────────────────────────────┼──────────────────────────────┐
         │                              │                              │
  ┌──────▼───────┐               ┌──────▼───────┐               ┌──────▼───────┐
  │PLANNER AGENT │               │  TASK GRAPH  │               │ EXEC ENGINE  │
  │(DAG Planning)│──────────────▶│ (DAG Engine) │──────────────▶│ (Observation │
  └──────────────┘               └──────────────┘               │     Loop)    │
                                                                └──────┬───────┘
                                                                       │
                                                       ┌───────────────┴───────────────┐
                                                       ▼                               ▼
                                             ┌───────────────────┐           ┌───────────────────┐
                                             │   AGENT ROUTER    │           │  MYSQL DATABASE   │
                                             │(Commander, Coder, │           │ (Executions,      │
                                             │Researcher,Reviewer│           │ Tasks, Events,    │
                                             └─────────┬─────────┘           │ Metrics, Approvals│
                                                       │                     └───────────────────┘
                                             ┌─────────▼─────────┐
                                             │   TOOL REGISTRY   │
                                             │(Calculator, Search│
                                             │ Filesystem, etc)  │
                                             └───────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python**: 3.12+ (or Python 3.14)
- **MySQL**: 8.0+ running on port `3306`
- **Flutter SDK**: 3.x+ (for frontend)

### 2. Database Migration (MySQL)
Ensure your MySQL server is running and configure settings in `backend/.env`. Execute all phase migration scripts:
```powershell
cd backend
$env:PYTHONPATH="."
python -m app.database.migrations.run_migrations
python -m app.database.migrations.phase2_execution_engine
python -m app.database.migrations.phase25_reliability
```

### 3. Backend Execution
Activate your Python virtual environment and start the FastAPI server:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.main
```
*The REST API will be available at `http://127.0.0.1:8000/docs`.*

### 4. Flutter Frontend Execution
Launch the Flutter application:
```powershell
cd frontend/flutter_app
flutter pub get
flutter run -d chrome
```

---

## 🧪 Testing & Evaluation Harness

ULTRON includes a comprehensive test suite covering backend logic, security, DAG resolution, crash recovery, state machines, and an end-to-end evaluation harness.

### Run Backend Unit & Integration Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
.\.venv\Scripts\pytest.exe ..\tests\backend -v
```

### Run End-to-End Evaluation Harness
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
.\.venv\Scripts\pytest.exe ..\tests\evaluation\test_eval_harness.py -v
```

### Run Complete Test Suite (40 Tests)
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
.\.venv\Scripts\pytest.exe ..\tests\backend ..\tests\evaluation -v
```

---

## 📊 API & Event Reference

### REST Endpoints (`/api/v1/executions`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/executions/` | Start a new execution (supports `idempotency_key`) |
| `GET` | `/api/v1/executions/` | List all executions for authenticated user |
| `GET` | `/api/v1/executions/{id}` | Detailed task graph, ordered event timeline, and event consistency report |
| `POST` | `/api/v1/executions/{id}/cancel` | Cancel an active execution and all pending/running sub-tasks |
| `POST` | `/api/v1/executions/{id}/resume` | Resume an interrupted execution from persisted DB state |
| `GET` | `/api/v1/executions/metrics` | Aggregate per-agent performance & review metrics |
| `POST` | `/api/v1/executions/approve` | Submit user approval or denial for pending sensitive tool execution |

### WebSocket Event Stream (`/ws/chat/{conversation_id}`)

WebSockets stream real-time JSON events containing `event_id`, `execution_id`, `timestamp`, `event_type`, and `payload`:
- `execution_started` / `execution_completed` / `execution_failed`
- `plan_created` / `task_created` / `task_started` / `task_completed` / `task_failed`
- `agent_started` / `agent_completed`
- `tool_started` / `tool_completed`
- `review_started` / `review_completed`
- `approval_required`

---

## 📁 Repository Structure

```
ULTRON/
├── backend/
│   ├── app/
│   │   ├── agents/          # Commander, Planner, Researcher, Coder, Reviewer
│   │   ├── ai/              # Provider-agnostic ModelManager (Gemini, OpenAI, Anthropic, Mock)
│   │   ├── api/             # FastAPI routers (Executions, Auth, Chat, Memory, Tasks, Tools)
│   │   ├── config/          # Environment configuration & logging setup
│   │   ├── core/            # UltronCore orchestration engine
│   │   ├── database/        # SQLAlchemy ORM models, repositories, and migration scripts
│   │   ├── engine/          # TaskGraph, AgentExecutionEngine, AgentRouter, ApprovalManager
│   │   ├── memory/          # Short-term conversation & long-term vector memory
│   │   ├── security/        # JWT auth, password hashing, filesystem sandbox
│   │   ├── tools/           # Tool registry (Calculator, WebSearch, Filesystem, Datetime)
│   │   └── main.py          # FastAPI application & WebSocket entrypoint
│   └── requirements.txt
├── frontend/
│   └── flutter_app/         # Flutter UI (ExecutionScreen, DetailScreen, TaskGraphWidget, etc.)
├── database/
│   └── schema.sql           # MySQL database DDL schema
└── tests/
    ├── backend/             # Unit tests (TaskGraph, Engine, State Machine, Idempotency, Metrics)
    └── evaluation/          # Deterministic eval dataset & E2E evaluation harness
```

---

## 📜 Documentation
- [Architecture Overview](file:///d:/ULTRON/docs/architecture/overview.md)
- [API Reference](file:///d:/ULTRON/docs/api/endpoints.md)
- [Database Schema](file:///d:/ULTRON/docs/database/schema.md)
- [Agent Architecture](file:///d:/ULTRON/docs/agents/architecture.md)
