# PROJECT ULTRON — Phase 9 Architecture & Implementation Plan

This document outlines the architecture, data models, event bus pipeline, decision engine, autonomy levels, and mobile integration plan for **Phase 9: Proactive Autonomous Agent + Event-Driven Intelligence**.

---

## 🎯 Architectural Intent & Boundary Principles

Phase 9 transforms ULTRON from a purely reactive system into a proactive, event-driven, personal autonomous agent. ULTRON can monitor triggers, detect events, reason using Context, Memory, and Knowledge, evaluate Autonomy Levels, decide whether to act, dispatch autonomous workflows via the existing Phase 7 `WorkflowOrchestrator`, and notify the user when appropriate.

### Key Governance Principles
1. **User Authority**: Autonomy determines *WHEN* to act within pre-authorized permissions. It does *NOT* grant ULTRON permission to grant itself new permissions.
2. **Reuse Existing Phase 1–8 Engines**: Phase 9 does NOT duplicate workflow execution, memory storage, knowledge search, or strategy selection. It delegates directly to:
   - `WorkflowOrchestrator` & `TaskScheduler` for workflow creation and execution.
   - `ApprovalCoordinator` for human-in-the-loop decisions.
   - `MemoryEngine` & `KnowledgeEngine` for context and evidence.
   - `LearningEngine` for tracking decision outcomes and user overrides.
   - `AgentRouter` for specialist agent selection.
3. **Hard Cooldown & Loop Limits**: All triggers, monitoring routines, and autonomous workflows are bounded by strict cooldown intervals, deduplication keys, rate limits, and maximum recursion depth to prevent infinite loops or notification storms.

---

## 🏗 Subsystem Components (`backend/app/autonomy/`)

1. **`contracts.py`**: Strongly typed Pydantic models for rules, triggers, events, decisions, actions, executions, notifications, and policy levels.
2. **`trigger.py` & `trigger_registry.py`**: Event sources (`SCHEDULE`, `INTERVAL`, `WEB_CHANGE`, `WORKFLOW_EVENT`, `KNOWLEDGE_UPDATE`, `FILE_CHANGE`, `MANUAL`, `SYSTEM_EVENT`). Triggers produce events; they do NOT directly execute code.
3. **`scheduler.py`**: Persistent, MySQL-backed scheduler surviving backend restarts with job locking and idempotency tracking.
4. **`monitor.py`**: Background monitors (`WebsiteMonitor` via Playwright, `WorkflowMonitor`, `KnowledgeMonitor`, `FileMonitor`, `SystemMonitor`) with semantic change detection.
5. **`event_bus.py` & `event_store.py`**: Event normalization, SHA-256 deduplication, priority rating, and audit trail persistence.
6. **`decision_engine.py`**: Proactive reasoning engine matching incoming events against user preferences, memories, knowledge, and policy levels. Produces decisions (`IGNORE`, `NOTIFY`, `ASK_USER`, `START_WORKFLOW`, `RUN_AUTONOMOUSLY`, `REQUIRE_APPROVAL`, `DENY`) with structured reasoning metadata.
7. **`autonomy_policy.py`**: Evaluates autonomy risk levels:
   - `LEVEL_0 = OBSERVE_ONLY`
   - `LEVEL_1 = NOTIFY_ONLY`
   - `LEVEL_2 = LOW_RISK_AUTONOMOUS_ACTION`
   - `LEVEL_3 = APPROVAL_REQUIRED` (Triggers `ApprovalCoordinator`)
   - `LEVEL_4 = FORBIDDEN`
8. **`cooldown.py` & `deduplication.py`**: Multi-level loop protection and rate limiting (`MAX_AUTONOMOUS_RUNS_PER_HOUR`, `MAX_NOTIFICATION_RATE`).
9. **`priority_engine.py`**: Evaluates event priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
10. **`notification_engine.py`**: User notification dispatcher without secret exposure.
11. **`autonomy_security.py`**: Tenant isolation, unauthorized execution blocking, permission escalation defense, and prompt injection isolation.
12. **`autonomy_manager.py` & `autonomy_executor.py`**: High-level manager orchestrating triggers, decision engine, workflow dispatches, and mobile WebSocket notifications.

---

## 🗄 Database & Persistence

- **Migration**: `backend/app/database/migrations/phase9_autonomy.py`.
- **Tables**: `autonomy_rules`, `autonomy_triggers`, `autonomy_events`, `autonomy_decisions`, `autonomy_executions`, `autonomy_notifications`, `autonomy_monitor_states`, `autonomy_policy_overrides`.
- **ORM Models**: Appended to `backend/app/database/models.py`.
- **Repository**: `backend/app/database/repositories/autonomy_repo.py` enforcing mandatory `user_id` multi-tenant filtering.

---

## 📱 Flutter Mobile UI Integration

- **Models & State**: `lib/models/autonomy_models.dart`, `lib/providers/autonomy_provider.dart`.
- **Dashboard**: `lib/screens/autonomy/autonomy_dashboard.dart` featuring active rule toggle, trigger status, recent activity timeline, and approval cards.
- **Rule Creation**: `lib/screens/autonomy/autonomy_rule_screen.dart`.
- **Navigation**: Integrated **⚡ Autonomy** into `home_screen.dart` bottom navigation bar.
