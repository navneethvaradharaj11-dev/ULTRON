# PROJECT ULTRON — Agentic AI Operating System

An advanced, production-grade **Agentic AI Operating System** featuring a DAG-based Task Graph execution engine, observation loops (`PLAN` → `ACT` → `OBSERVE` → `EVALUATE`), an autonomous **Playwright Chromium Browser Agent (Phase 3 & 3.1)**, an autonomous **Code Intelligence & Secure Execution Sandbox (Phase 4)**, a **Perception Engine & Controlled Computer Interaction System (Phase 5)**, structured multi-agent orchestration, backend-validated approval security, process crash recovery, deterministic evaluation harness, per-agent performance metrics, real-time WebSocket event streaming, and a Flutter cross-platform UI.

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
  - **Deterministic Backend Test Suite (109 / 109 PASSED)**: Test scenarios covering calculations, multi-step research, code generation, real Chromium browser interactions, browser security policies, sandbox isolation, perception engine, visual grounding, controlled computer interaction, computer security, and E2E evaluation workflows.
  - **Flutter Widget Test Suite (7 / 7 PASSED)**: Widget test suite covering code intelligence and perception widgets with 0 `flutter analyze` errors.
  - **Per-Agent Metrics (`execution_metrics`)**: Tracks duration, success/failure rate, retries, and review confidence per agent.
- **Interactive Flutter UI**:
  - **Execution History & Tabbed Goal View**: Live progress monitoring, goal submission, inline Cancel/Resume actions.
  - **Task Graph & Event Timeline**: Detailed visual task status cards and chronological event sequence timeline with payload previews and consistency badge.
  - **Browser Agent Screen**: Real-time browser session monitoring, viewport screenshot preview, navigation controls, live DOM action history cards (`BrowserActionCard`), and research source citation cards (`SourceCard`).
  - **Code Intelligence Workspace Screen**: Integrated code editor, terminal output console, file tree, test execution results, and artifact viewer.
  - **Perception & Computer Session Screen**: Viewport screenshot viewer, visual bounding overlay, detected UI component cards, computer action timeline, and sensitive action approval dialog.
  - **Agent Analytics Tab**: Visual linear progress bars tracking success rate and average execution time per agent.
- **Security & Sandboxing**: Server-side tool approval prompts, strict filesystem sandboxing, controlled computer bounds check, prompt injection isolation, and JWT-authenticated WebSockets.

---

## 🏗️ Architecture & System Topology

```
                       ┌──────────────────────────────────┐
                       │     FLUTTER CROSS-PLATFORM UI    │
                       │ (Executions / History / Code /   │
                       │   Browser / Perception Screens)  │
                       └────────────────┬─────────────────┘
                                        │
                                   REST / WS
                                        │
                       ┌────────────────▼─────────────────┐
                       │       FASTAPI BACKEND API        │
                       │ (Executions, Auth, Chat, Code,   │
                       │   Browser, Computer, Perception) │
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
                                             │Computer, Reviewer)│           │ Browser Sessions, │
                                             └─────────┬─────────┘           │ Computer Sessions)│
                                                       │                     └───────────────────┘
                                   ┌───────────────────┼───────────────────┐
                                   ▼                   ▼                   ▼
                         ┌───────────────────┐ ┌───────────────┐ ┌───────────────────┐
                         │   TOOL REGISTRY   │ │PERCEPTION ENG │ │ BROWSER / COMPUTER│
                         │ (Browser, Code,   │ │(DOM, A11y, OCR│ │    SECURITY       │
                         │  Calc, Perception)│ │ Vision Fusion)│ │ (Bounds, Redact,  │
                         └─────────┬─────────┘ └───────┬───────┘ │  Path Sandbox)    │
                                   │                   │         └─────────┬─────────┘
                                   └───────────────────┼───────────────────┘
                                                       ▼
                                             ┌───────────────────┐
                                             │ COMPUTER / BROWSER│
                                             │    MANAGERS       │
                                             │(Playwright Async, │
                                             │ Input Executor)   │
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
Ensure your MySQL server is running and configure settings in `backend/.env`. Execute all migration scripts:
```powershell
cd backend
$env:PYTHONPATH="."
python -m app.database.migrations.run_migrations
python -m app.database.migrations.phase2_execution_engine
python -m app.database.migrations.phase25_reliability
python -m app.database.migrations.phase3_browser
python -m app.database.migrations.phase4_code
python -m app.database.migrations.phase5_perception
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

ULTRON includes a comprehensive test suite covering unit logic, security, DAG resolution, crash recovery, state machines, browser agentic workflows, Playwright security boundaries, code intelligence sandbox isolation, multi-language compilation/testing, perception engine, visual grounding, controlled computer interaction, and an end-to-end evaluation harness.

### Run Backend Unit & Security Tests
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

### Run Phase 4 Code Intelligence & Sandbox Security Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\code -v
```

### Run Phase 5 Perception & Computer Security Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\perception -v
```

### Run End-to-End Evaluation Harness & Integration Tests
```powershell
cd backend
$env:PYTHONPATH="d:\ULTRON\backend"
python -m pytest ..\tests\evaluation ..\tests\integration -v
```

### Run Complete Test Suite (109 Tests — 100% Passing)
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

### REST Endpoints — Code Intelligence (`/api/v1/code`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/code/compile` | Compile code file in sandbox (C, C++, Java, JS, Python) |
| `POST` | `/api/v1/code/execute` | Safely execute compiled binary/script inside sandbox container |
| `POST` | `/api/v1/code/test` | Run unit test suite against sandbox workspace |

### REST Endpoints — Perception Engine (`/api/v1/perception`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/perception/perceive` | Perceive UI state fusing DOM, Accessibility Tree, OCR, and Vision Analyzer |
| `POST` | `/api/v1/perception/ground` | Ground natural language instruction to visual target with bounding box |

### REST Endpoints — Controlled Computer Interaction (`/api/v1/computer`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/computer/sessions` | Create a new controlled computer interaction session |
| `GET` | `/api/v1/computer/sessions` | List active computer sessions for user |
| `POST` | `/api/v1/computer/sessions/{id}/actions` | Dispatch controlled mouse (`CLICK`, `SCROLL`) or keyboard (`TYPE`) action |
| `POST` | `/api/v1/computer/actions/approve` | Explicitly approve pending sensitive computer action |
| `POST` | `/api/v1/computer/actions/reject` | Explicitly reject pending sensitive computer action |

### WebSocket Event Stream (`/ws/chat/{conversation_id}`)

WebSockets stream real-time JSON events containing `event_id`, `execution_id`, `timestamp`, `event_type`, and `payload`:
- `execution_started` / `execution_completed` / `execution_failed`
- `plan_created` / `task_created` / `task_started` / `task_completed` / `task_failed`
- `agent_started` / `agent_completed`
- `tool_started` / `tool_completed`
- `browser_session_created` / `browser_navigated` / `browser_action_executed` / `browser_screenshot_captured` / `browser_session_closed`
- `perception_started` / `perception_completed` / `visual_element_detected` / `visual_target_grounded`
- `computer_session_started` / `computer_action_requested` / `computer_action_approved` / `computer_action_completed` / `computer_action_failed`
- `review_started` / `review_completed`
- `approval_required`

---

## 📁 Repository Structure

```
ULTRON/
├── backend/
│   ├── app/
│   │   ├── agents/          # Commander, Planner, Researcher, Coder, CodeAgent, ComputerAgent, Reviewer, BrowserAgent
│   │   ├── ai/              # Provider-agnostic ModelManager (Gemini, OpenAI, Anthropic, Mock)
│   │   ├── api/             # FastAPI routers (Executions, Auth, Chat, Memory, Tasks, Tools, Browser, Research, Code, Computer, Perception)
│   │   ├── browser/         # BrowserManager, BrowserSession, Navigation, PageActions, ElementFinder
│   │   ├── computer/        # ComputerManager, ComputerSession, MouseController, KeyboardController, InputController, ComputerPolicy, ActionExecutor
│   │   ├── config/          # Environment configuration & logging setup
│   │   ├── core/            # UltronCore orchestration engine
│   │   ├── database/        # SQLAlchemy ORM models, repositories, and migration scripts (Phases 1-5 included)
│   │   ├── engine/          # TaskGraph, AgentExecutionEngine, AgentRouter, ApprovalManager
│   │   ├── memory/          # Short-term conversation & long-term vector memory
│   │   ├── perception/      # ScreenshotCapture, VisionAnalyzer, UIDetector, VisualGrounder, OCREngine, AccessibilityTree, PerceptionFusion, PerceptionEngine
│   │   ├── sandbox/         # Multi-language sandbox runtime & process isolation manager
│   │   ├── security/        # JWT auth, password hashing, filesystem sandbox, BrowserSecurity, ComputerSecurityValidator
│   │   ├── tools/           # Tool registry (Browser, Code, Computer, Perception, Calculator, WebSearch, Filesystem)
│   │   └── main.py          # FastAPI application & WebSocket entrypoint
│   └── requirements.txt
├── frontend/
│   └── flutter_app/         # Flutter UI (ExecutionScreen, DetailScreen, CodeScreen, PerceptionScreen, ComputerSessionScreen, BrowserScreen, etc.)
├── database/
│   └── schema.sql           # MySQL database DDL schema (Phases 1-5)
├── docs/
│   ├── agents/              # Agent architecture documentation
│   ├── api/                 # Endpoint documentation
│   ├── architecture/        # Topology and design overviews
│   ├── audits/              # Phase 3.1, Phase 4, Phase 5 Audit Reports
│   ├── database/            # Database schema documentation
│   └── security/            # Security & sandbox policies
├── web/                     # Injected JavaScript bridges (page_bridge.js, content_extractor.js, browser_agent.js)
└── tests/
    ├── backend/             # Unit tests (TaskGraph, Engine, State Machine, Idempotency, Metrics)
    ├── browser/             # Browser agentic & security tests
    ├── code/                # Code agentic & sandbox security tests
    ├── evaluation/          # Deterministic eval dataset & E2E evaluation harness
    ├── integration/         # E2E Playwright Chromium & Computer Vision integration test suite
    └── perception/          # Perception security & agentic interaction tests
```

---

## 📜 Documentation
- [Phase 5 Perception Engine Audit Report](file:///d:/ULTRON/docs/audits/phase5-perception-audit.md)
- [Phase 4 Code Intelligence Audit Report](file:///d:/ULTRON/docs/audits/phase4-code-agent-audit.md)
- [Phase 3.1 Real Browser Runtime Audit Report](file:///d:/ULTRON/docs/audits/phase3.1-browser-runtime-audit.md)
- [Phase 5 Perception Architecture Overview](file:///d:/ULTRON/docs/architecture/phase5-perception.md)
- [Phase 5 Controlled Computer Interaction Policy](file:///d:/ULTRON/docs/security/phase5-computer-security.md)
- [API Reference](file:///d:/ULTRON/docs/api/computer.md)
- [Database Schema](file:///d:/ULTRON/docs/database/phase5-schema.md)
- [Agent Architecture](file:///d:/ULTRON/docs/agents/computer_agent.md)
