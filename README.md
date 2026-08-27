# PROJECT ULTRON — Phase 1

An advanced modular Agentic AI Operating System capable of multi-agent collaboration, planning, persistent memory, safe tool execution, real-time WebSocket event streaming, and a Flutter cross-platform UI.

## Architecture & Tech Stack

- **Frontend**: Dart / Flutter
- **Backend / AI Engine**: Python 3.14 / FastAPI
- **Web Layer**: JavaScript / HTML / CSS
- **Primary Database**: MySQL
- **Communication**: REST API + WebSocket (Structured event streaming)

## System Overview

```
                      ┌──────────────────┐
                      │    FLUTTER UI    │
                      │  (Dart/Flutter)  │
                      └────────┬─────────┘
                               │
                          REST / WS
                               │
                      ┌────────▼─────────┐
                      │  FASTAPI BACKEND │
                      │  (Python 3.14)   │
                      └────────┬─────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
     ┌──────▼───────┐   ┌──────▼───────┐   ┌──────▼───────┐
     │ ULTRON CORE  │   │ AGENT ENGINE │   │ MEMORY ENGINE│
     │ Orchestrator │   │ (Commander,  │   │ (Short/Long) │
     └──────┬───────┘   │ Planner, etc)│   └──────┬───────┘
            │           └──────┬───────┘          │
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                      ┌────────▼─────────┐
                      │   TOOL ENGINE    │
                      │ (ToolRegistry)   │
                      └────────┬─────────┘
                               │
                      ┌────────▼─────────┐
                      │  MYSQL DATABASE  │
                      │  (ultron_db)     │
                      └──────────────────┘
```

## Quick Start

### 1. Database Setup (MySQL)
Ensure local MySQL service is running on port 3306. Configure `MYSQL_USER` and `MYSQL_PASSWORD` in `backend/.env`. Run the migration runner:
```bash
cd backend
python -m app.database.migrations.run_migrations
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate virtualenv (Windows PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python -m app.main
```

### 3. Flutter Frontend Setup
```bash
cd frontend/flutter_app
flutter pub get
flutter run -d chrome
```

### 4. Web Browser Layer
Open `web/index.html` in your web browser.

## Documentation
- [Architecture Overview](file:///d:/ULTRON/docs/architecture/overview.md)
- [API Reference](file:///d:/ULTRON/docs/api/endpoints.md)
- [Database Schema](file:///d:/ULTRON/docs/database/schema.md)
- [Agent Architecture](file:///d:/ULTRON/docs/agents/architecture.md)
