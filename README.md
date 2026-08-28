# PROJECT ULTRON — Agentic AI Operating System

An advanced, production-grade **Agentic AI Operating System** featuring a DAG-based Task Graph execution engine, observation loops (`PLAN` → `ACT` → `OBSERVE` → `EVALUATE`), an autonomous **Playwright Chromium Browser Agent (Phase 3 & 3.1)**, an autonomous **Code Intelligence & Secure Execution Sandbox (Phase 4)**, structured multi-agent orchestration, backend-validated approval security, process crash recovery, deterministic evaluation harness, per-agent performance metrics, real-time WebSocket event streaming, and a Flutter cross-platform UI.

---

## 🌟 Key Highlights & Capabilities

- **Phase 5 Perception Engine & Controlled Computer Interaction**:
  - **Specialist ComputerAgent**: Autonomous perception-enabled agent operating via `OBSERVE` → `PERCEIVE` → `GROUND` → `ACT` → `VERIFY` → `RECOVER` visual loop.
  - **Multi-Modal Perception Engine**: Fuses DOM, Accessibility Tree, OCR text, and Vision Component Detection into strongly typed visual targets with bounding boxes and confidence scores.
  - **Visual Grounding Engine**: Converts natural-language instructions into visual targets with automatic candidate ranking and fallback handling.
  - **Controlled Input Engine**: Controlled mouse (`MOVE`, `CLICK`, `DOUBLE_CLICK`, `RIGHT_CLICK`, `SCROLL`, `DRAG`) and keyboard (`TYPE`, `PRESS_KEY`, `HOTKEY`) interaction scoped to viewport bounds.
  - **Safety Policy & Approval Guard**: Server-side action rate limits (`MAX_COMPUTER_ACTIONS = 20`), coordinate bounds validation, low-confidence rejection (`< 0.60`), high-impact sensitive action approval (`REQUIRES_APPROVAL`), and `UNTRUSTED VISUAL DATA` prompt injection defense.
  - **Flutter Perception & Interaction Workspace**: Screen viewport capture viewer, visual bounding box overlay, detected UI component cards, computer action timeline, sensitive action approval dialog, and live perception confidence indicator.
- **Phase 4 Code Intelligence & Secure Execution Sandbox**:
  - **Specialist CodeAgent**: Autonomous agent operating via structured Pydantic action contracts (`CREATE_FILE`, `UPDATE_FILE`, `COMPILE`, `EXECUTE`, `RUN_TESTS`) with self-debugging observation loops.
  - **Pluggable Language Runtimes**: Multi-language runtime system supporting Python, JavaScript, C, and C++.
  - **Multi-Layer Process & Network Sandbox**: Fail-closed execution environment enforcing path jail isolation, forbidden root access (`backend`, `app`, `.env`), default `DENY_ALL` network policy, and server-side CPU, RAM, timeout, and output size limits.
  - **Flutter Code Intelligence Workspace**: Integrated code editor with line numbers, syntax styling, tab management, diff viewer, terminal stdout/stderr console, timeline events, test results, and downloadable artifacts.
- **DAG Task Graph Engine (`TaskGraph` / `TaskNode`)**: Dynamically resolves sub-task dependencies using topological sorting and Kahn's algorithm cycle validation.
- **Autonomous Playwright Chromium Browser Agent (Phase 3 & 3.1)**:
  - **Real Headless Chromium Engine**: Spawns isolated `BrowserContext` instances via Playwright (v1.62.0) capable of executing dynamic JavaScript, observing dynamic DOM updates, interacting with elements, and rendering viewport screenshots.
  - **Browser Agent (`BrowserAgent`)**: Specialized agent supporting URL navigation (`goto`), element manipulation (`click`, `type`, `select`), history navigation (`go_back`, `go_forward`, `reload`), page DOM reading, screenshot capture, and structured web research synthesis.
- **Specialized Multi-Agent Swarm**:
  - **Commander**: Intent recognition & high-level strategy coordination.
  - **Planner**: Generates structured DAG plans with strict Pydantic schema validation.
  - **Researcher / Browser Agent**: Autonomous web browsing, DOM navigation, and multi-source research synthesis.
  - **Coder / CodeAgent**: Multi-language code generation, structured file edits, compilation, testing, and self-debugging observation loops.
  - **ComputerAgent**: Multi-modal perception, UI component detection, visual grounding, and controlled mouse/keyboard interaction.
  - **Reviewer**: Evaluates task output quality, returning structured confidence scores, issue lists, and approval/rejection decisions.
- **Evaluation Harness & Metrics (100% PASS RATE Verified)**:
  - **Deterministic Test Suite (109 / 109 PASSED)**: Backend test suite covering calculations, multi-step research, code generation, real Chromium browser interactions, browser security policies, sandbox isolation, perception engine, visual grounding, controlled computer interaction, computer security, and E2E evaluation workflows.
  - **Flutter Test Suite (7 / 7 PASSED)**: Widget test suite covering code intelligence and perception widgets with 0 `flutter analyze` errors.
  - **Per-Agent Metrics (`execution_metrics`)**: Tracks duration, success/failure rate, retries, and review confidence per agent.
- **Interactive Flutter UI**:
  - **Execution History & Tabbed Goal View**: Live progress monitoring, goal submission, inline Cancel/Resume actions.
  - **Task Graph & Event Timeline**: Detailed visual task status cards and chronological event sequence timeline with payload previews and consistency badge.
  - **Browser Agent Screen**: Real-time browser session monitoring, viewport screenshot preview, navigation controls, live DOM action history cards (`BrowserActionCard`), and research source citation cards (`SourceCard`).
  - **Perception & Computer Session Screen**: Viewport screenshot viewer, visual bounding overlay, detected UI component cards, computer action timeline, and sensitive action approval dialog.
  - **Agent Analytics Tab**: Visual linear progress bars tracking success rate and average execution time per agent.
- **Security & Sandboxing**: Server-side tool approval prompts, strict filesystem sandboxing, controlled computer bounds check, prompt injection isolation, and JWT-authenticated WebSockets.

---

## 🏗️ Architecture & System Topology

```
                       ┌──────────────────────────────────┐
                       │     FLUTTER CROSS-PLATFORM UI    │
                       │ (Executions / History / Browser) │
                       └────────────────┬─────────────────┘
                                        │
                                   REST / WS
                                        │
                       ┌────────────────▼─────────────────┐
                       │       FASTAPI BACKEND API        │
                       │ (Executions, Chat, Auth, Browser)│
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
                                             │Researcher,Browser,│           │ Tasks, Events,    │
                                             │     Reviewer)     │           │ Browser Sessions) │
                                             └─────────┬─────────┘           └───────────────────┘
                                                       │
                                   ┌───────────────────┴───────────────────┐
                                   ▼                                       ▼
                         ┌───────────────────┐                   ┌───────────────────┐
                         │   TOOL REGISTRY   │                   │ BROWSER SECURITY  │
                         │ (Browser, Calc,   │                   │ (SSRF, Protocol,  │
                         │  Search, Sandbox) │                   │ Redaction, Safe)  │
                         └─────────┬─────────┘                   └─────────┬─────────┘
                                   │                                       │
                                   └───────────────────┬───────────────────┘
                                                       ▼
                                             ┌───────────────────┐
                                             │  BROWSER MANAGER  │
                                             │ (Playwright Async │
                                             │ Chromium Instance)│
                                             └───────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python**: 3.12+ (or Python 3.14)
- **Playwright Chromium Binary**: Installed via `playwright install chromium`
- **MySQL**: 8.0+ running on port `3306`
- **Flutter SDK**: 3.x+ (for frontend)

### 2. Database Migration (MySQL)
Ensure your MySQL server is running and configure settings in `backend/.env`. Execute all migration scripts including Phase 3 Browser support:
```powershell
cd backend
$env:PYTHONPATH="."
python -m app.database.migrations.run_migrations
python -m app.database.migrations.phase2_execution_engine
python -m app.database.migrations.phase25_reliability
python -m app.database.migrations.phase3_browser
```

### 3. Backend Execution
Activate your Python virtual environment and start the FastAPI server:
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
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

ULTRON includes a comprehensive test suite covering unit logic, security, DAG resolution, crash recovery, state machines, browser agentic workflows, Playwright security boundaries, and an end-to-end evaluation harness.

### Run Backend Unit & Integration Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\backend -v
```

### Run Phase 3 Browser Agent & Security Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\browser -v
```

### Run End-to-End Evaluation Harness
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\evaluation\test_eval_harness.py -v
```

### Run Complete Test Suite (56 Tests — 100% Passing)
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests -v
```

---

## 📊 API & Event Reference

### REST Endpoints — Executions (`/api/v1/executions`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/executions/` | Start a new execution (supports `idempotency_key`) |
| `GET` | `/api/v1/executions/` | List all executions for authenticated user |
| `GET` | `/api/v1/executions/{id}` | Detailed task graph, ordered event timeline, and event consistency report |
| `POST` | `/api/v1/executions/{id}/cancel` | Cancel an active execution and all pending/running sub-tasks |
| `POST` | `/api/v1/executions/{id}/resume` | Resume an interrupted execution from persisted DB state |
| `GET` | `/api/v1/executions/metrics` | Aggregate per-agent performance & review metrics |
| `POST` | `/api/v1/executions/approve` | Submit user approval or denial for pending sensitive tool execution |

### REST Endpoints — Browser & Web Research (`/api/v1/browser`, `/api/v1/research`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/browser/sessions` | Create a new isolated Playwright Chromium browser session |
| `DELETE` | `/api/v1/browser/sessions/{session_id}` | Teardown and close an active browser session |
| `POST` | `/api/v1/browser/navigate` | Navigate browser session to specified URL |
| `POST` | `/api/v1/browser/actions/click` | Click DOM element by CSS selector |
| `POST` | `/api/v1/browser/actions/type` | Input text string into DOM target element |
| `POST` | `/api/v1/browser/actions/select` | Select option value in `<select>` dropdown |
| `GET` | `/api/v1/browser/sessions/{session_id}/page` | Read rendered page title and DOM structure |
| `GET` | `/api/v1/browser/sessions/{session_id}/screenshot` | Render Base64 PNG viewport screenshot |
| `POST` | `/api/v1/research/web` | Run autonomous multi-step browser web research agent |

### WebSocket Event Stream (`/ws/chat/{conversation_id}`)

WebSockets stream real-time JSON events containing `event_id`, `execution_id`, `timestamp`, `event_type`, and `payload`:
- `execution_started` / `execution_completed` / `execution_failed`
- `plan_created` / `task_created` / `task_started` / `task_completed` / `task_failed`
- `agent_started` / `agent_completed`
- `tool_started` / `tool_completed`
- `browser_session_created` / `browser_navigated` / `browser_action_executed` / `browser_screenshot_captured` / `browser_session_closed`
- `review_started` / `review_completed`
- `approval_required`

---

## 📁 Repository Structure

```
ULTRON/
├── backend/
│   ├── app/
│   │   ├── agents/          # Commander, Planner, Researcher, Coder, Reviewer, BrowserAgent
│   │   ├── ai/              # Provider-agnostic ModelManager (Gemini, OpenAI, Anthropic, Mock)
│   │   ├── api/             # FastAPI routers (Executions, Auth, Chat, Memory, Tasks, Tools, Browser, Research)
│   │   ├── browser/         # BrowserManager, BrowserSession, Navigation, PageActions, ElementFinder
│   │   ├── config/          # Environment configuration & logging setup
│   │   ├── core/            # UltronCore orchestration engine
│   │   ├── database/        # SQLAlchemy ORM models, repositories, and migration scripts (Phase 3 included)
│   │   ├── engine/          # TaskGraph, AgentExecutionEngine, AgentRouter, ApprovalManager
│   │   ├── memory/          # Short-term conversation & long-term vector memory
│   │   ├── security/        # JWT auth, password hashing, filesystem sandbox, BrowserSecurity
│   │   ├── tools/           # Tool registry (Browser tools, Calculator, WebSearch, Filesystem)
│   │   └── main.py          # FastAPI application & WebSocket entrypoint
│   └── requirements.txt
├── frontend/
│   └── flutter_app/         # Flutter UI (ExecutionScreen, DetailScreen, TaskGraphWidget, BrowserScreen, BrowserView, etc.)
├── database/
│   └── schema.sql           # MySQL database DDL schema (Phases 1, 2, 2.5, 3)
├── docs/
│   ├── agents/              # Agent architecture documentation
│   ├── api/                 # Endpoint documentation
│   ├── architecture/        # Topology and design overviews
│   ├── audits/              # Phase 3.1 Real Browser Runtime Audit Report
│   └── database/            # Database schema documentation
├── web/                     # Injected JavaScript bridges (page_bridge.js, content_extractor.js, browser_agent.js)
└── tests/
    ├── backend/             # Unit tests (TaskGraph, Engine, State Machine, Idempotency, Metrics)
    ├── browser/             # Browser agentic & security tests
    ├── evaluation/          # Deterministic eval dataset & E2E evaluation harness
    └── integration/         # E2E Playwright Chromium browser integration test suite
```

---

## 📜 Documentation
- [Phase 3.1 Real Browser Runtime Audit Report](file:///d:/ULTRON/docs/audits/phase3.1-browser-runtime-audit.md)
- [Architecture Overview](file:///d:/ULTRON/docs/architecture/overview.md)
- [API Reference](file:///d:/ULTRON/docs/api/endpoints.md)
- [Database Schema](file:///d:/ULTRON/docs/database/schema.md)
- [Agent Architecture](file:///d:/ULTRON/docs/agents/architecture.md)

