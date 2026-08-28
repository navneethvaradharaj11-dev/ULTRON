# PROJECT ULTRON — Personal Agent Operating System

An advanced, production-grade **Personal Agent Operating System** unifying 10 core autonomous AI capabilities into a single, cohesive agentic runtime. ULTRON empowers users to define high-level intentions ("ULTRON, handle this") and autonomously plan, execute, observe, evaluate, recover, learn, and deliver verified results across web browsing, multi-language code sandboxes, desktop perception, long-term memory, multimodal knowledge bases, and event-driven background triggers via Flutter mobile remote control.

---

## 🌟 Key Capabilities Across Phases 1–10

### 🧠 Phase 10 — Personal Agent Operating System & Unified Runtime
- **Unified Command Interface ("ULTRON, handle this")**: Natural language commands via `POST /api/v1/ultron/command` automatically pass through intent parsing, context scoping, capability discovery, and resource budget checks into an autonomous workflow DAG.
- **Structured Intent Engine (`IntentEngine`)**: Converts user messages into structured goals with risk ratings, urgency scores, and required capability dependencies.
- **Dynamic Capability Registry (`CapabilityRegistry`)**: Real-time health monitoring and availability discovery for all 11 system capabilities (`memory`, `knowledge`, `research`, `browser`, `computer`, `code`, `sandbox`, `workflows`, `autonomy`, `learning`, `notifications`).
- **Scoped Personal Context Engine (`PersonalContextEngine`)**: Scopes user preferences, durable facts, project contexts, knowledge workspaces, and workflow history without prompt pollution.
- **Bounded Resource Budget (`ResourceBudgetTracker`)**: Enforces safety limits per workflow (max tool calls, browser steps, runtime seconds, and sandbox memory).
- **Unified Security Gate (`UnifiedSecurityGate`)**: Single security gate enforcing authentication, multi-tenant `user_id` isolation, capability permission limits, risk evaluation, and human approval gates across all 10 phases.
- **Flutter Command Center (`UltronCommandCenter`)**: Command-first mobile UX with live activity timeline stream, capability status header, and approval center.

### ⚡ Phase 9 — Proactive Autonomous Agent & Event-Driven Intelligence
- **Event-Driven Triggers**: Supports 8 trigger types (`SCHEDULE`, `INTERVAL`, `WEB_CHANGE`, `WORKFLOW_EVENT`, `KNOWLEDGE_UPDATE`, `FILE_CHANGE`, `MANUAL`, `SYSTEM_EVENT`).
- **Persistent MySQL Scheduler**: Backend restart survival with job locking, idempotency tracking, and interval schedule processing.
- **Playwright Website Monitor**: Semantic change detection for monitored web pages using content hash comparisons.
- **Deduplication & Cooldown Manager**: SHA-256 event deduplication and strict cooldown windows preventing notification storms or recursive execution loops.

### 📚 Phase 8 — Multimodal Knowledge Fabric & Intelligent Workspace
- **Multimodal Parsers**: Ingests PDF, DOCX, XLSX/CSV, PPTX, TXT, Markdown, codebases, images, audio, and video files.
- **Hybrid Search Engine**: Combines BM25 keyword matching with vector semantic similarity search and reranking.
- **Provenance Citations**: Generates traceable document citations (e.g., `[1] study_notes.txt — Page 1`).

### 📋 Phase 7 — Autonomous Workflow Orchestrator
- **Central Workflow Lifecycle**: Manages complete state machine transitions (`CREATED` $\rightarrow$ `UNDERSTANDING` $\rightarrow$ `PLANNING` $\rightarrow$ `READY` $\rightarrow$ `RUNNING` $\rightarrow$ `VERIFYING` $\rightarrow$ `COMPLETED`).
- **Crash Recovery & Checkpointing**: `CheckpointManager`, `FailureManager`, `RecoveryEngine`, and `ReplanningEngine` for state recovery after failures.

### 🧠 Phase 6 — Long-Term Memory, Strategy & Learning Engine
- **Durable Fact Memory**: Stores facts, preferences, and session summaries with confidence scoring, recency decay, and conflict resolution.
- **Adaptive Strategy & Learning**: `StrategyEngine` selects optimal execution strategies; `LearningEngine` tracks agent metrics and user feedback.

### 👁️ Phase 5 — Perception & Controlled Computer Interaction
- **Visual Grounding & OCR**: Desktop viewport capture, OCR text extraction, UI element detection, and bounding box grounding.
- **Computer Session Security**: `ComputerSecurityValidator` enforces coordinate bounds and multi-tenant session isolation.

### 💻 Phase 4 — Code Intelligence & Secure Multi-Language Sandbox Jail
- **Multi-Language Runtime Support**: Compiles and executes Python, JavaScript (Node.js), C (GCC), and C++ (G++).
- **Process & Filesystem Sandbox**: Confines execution inside isolated workspace directories, blocking path traversal (`../`, `C:\Windows`, `.env`) and network access (`DENY_ALL`).

### 🌐 Phase 3 & 3.1 — Real Playwright Chromium Browser Agent
- **Headless & Headed Playwright Engine**: Launches isolated Playwright Chromium browser contexts for page navigation, element interaction, screenshot rendering, and web research.
- **Browser Policy**: Enforces domain whitelisting and blocks unsafe URL protocols (`file://`, `javascript:`, `data:`).

### 🔀 Phase 2 — Execution Engine & DAG Task Graph
- **Topological DAG Scheduler**: Dynamically resolves task dependencies, cycle detection, and parallel group execution.
- **Specialist Agent Router**: Maps tasks to `Commander`, `Planner`, `Researcher`, `Coder`, `CodeAgent`, `BrowserAgent`, `ComputerAgent`, `Reviewer`, `LearningAgent`, and `KnowledgeAgent`.

### 🔒 Phase 1 — Core Infrastructure, Authentication & Persistence
- **Security & Multi-Tenancy**: JWT authentication with bcrypt hashing and mandatory `user_id` database scoping.
- **Database Engine**: Async SQLAlchemy 2.0 with MySQL persistence and SQLite test fallback.

---

## 🏗️ System Architecture & Pipeline

```text
                     👤 USER / FLUTTER MOBILE APP
                                   │
                    POST /api/v1/ultron/command
                                   │
                                   ▼
                       🧠 ULTRON CORE RUNTIME
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
IntentEngine              PersonalContextEngine        CapabilityRegistry
(Natural Intent Parsing)  (Durable Facts & Preferences) (Health & Availability)
       │                           │                           │
       └───────────────────────────┼───────────────────────────┘
                                   ▼
                     UnifiedSecurityGate & ResourceBudget
                                   │
                                   ▼
                       WorkflowOrchestrator (Phase 7)
                                   │
                                   ▼
                   AgentCoordinator & Specialist Agents
       (BrowserAgent, CodeAgent, ComputerAgent, KnowledgeAgent, etc.)
                                   │
                                   ▼
                    Flutter Mobile Activity Stream
```

---

## 📊 Verification Baseline

- **Backend Pytest Regression Suite**: **200 / 200 PASSED** (100% pass rate).
- **Phase 10.1 Real-World Monster Mission Suite**: **8 / 8 PASSED** ([`test_phase10_1_real_world.py`](file:///d:/ULTRON/tests/acceptance/test_phase10_1_real_world.py)).
- **Consolidated Security Suite**: **5 / 5 PASSED** ([`test_consolidated_security.py`](file:///d:/ULTRON/tests/security/test_consolidated_security.py)).
- **Phase 10 Real-World Acceptance Suite**: **12 / 12 PASSED** ([`test_phase10_real_world.py`](file:///d:/ULTRON/tests/acceptance/test_phase10_real_world.py)).
- **Phase 9 Acceptance Suite**: **16 / 16 PASSED** ([`test_phase9_real_world.py`](file:///d:/ULTRON/tests/acceptance/test_phase9_real_world.py)).
- **Phase 1–8 Real-World Acceptance Suite**: **9 / 9 PASSED** ([`test_real_world_acceptance.py`](file:///d:/ULTRON/tests/acceptance/test_real_world_acceptance.py)).
- **Flutter Mobile Analysis**: `flutter analyze` = **0 ERRORS** (All 106 items are minor informational hints).
- **Flutter Widget Test Suite**: `flutter test` = **8 / 8 PASSED**.
- **Audit Verdict**: Documented in [`docs/audits/phase10.1-production-hardening-audit.md`](file:///d:/ULTRON/docs/audits/phase10.1-production-hardening-audit.md) (`PRODUCTION READY`).


---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- Flutter SDK 3.x
- Node.js & Playwright (for Browser Agent)

### Backend Setup
```powershell
# Navigate to project directory
cd D:\ULTRON

# Activate virtual environment
.\backend\.venv\Scripts\Activate.ps1

# Run tests
$env:PYTHONPATH="backend"
.\backend\.venv\Scripts\pytest.exe tests/ -v

# Start FastAPI server
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Mobile App Setup
```powershell
cd D:\ULTRON\frontend\flutter_app

# Run Flutter static analysis
flutter analyze

# Run Flutter widget tests
flutter test

# Run application
flutter run
```

---

## 📄 License & Attribution
PROJECT ULTRON — Agentic AI Operating System. Built with Python, FastAPI, SQLAlchemy, Playwright, MySQL, and Flutter.
