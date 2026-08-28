# Phase 9 Architecture — Proactive Autonomous Agent

## Overview
Phase 9 transforms ULTRON into a proactive, event-driven personal autonomous agent. ULTRON monitors user-configured triggers, evaluates incoming events, applies Context, Memory, and Knowledge, checks Autonomy Levels, and dispatches workflow tasks via the Phase 7 `WorkflowOrchestrator`.

---

## Core Components
- `AutonomyManager`: Orchestrates triggers, events, decision engine, and execution.
- `PersistentScheduler`: MySQL-backed scheduler surviving backend restarts.
- `WebsiteMonitor`: Playwright-based website monitor with semantic change detection.
- `EventBus`: Pipeline for event normalization, deduplication, and prioritization.
- `ProactiveDecisionEngine`: Synthesizes policy, context, memory, and evidence into structured decisions.
- `AutonomyPolicyEngine`: Risk evaluator assigning `LEVEL_0` to `LEVEL_4`.
- `NotificationEngine`: Mobile notification dispatcher with secret sanitization.
