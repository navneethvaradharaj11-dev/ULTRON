# Phase 4 Architecture: Code Intelligence & Secure Execution Sandbox

## Overview
Phase 4 introduces autonomous code intelligence capabilities into ULTRON. The system allows ULTRON to understand user software requests, plan task graphs, create and edit multi-file codebases (Python, JavaScript, C, C++), execute code inside isolated sandboxes, observe output, self-debug, execute test suites, perform code reviews, and deliver verified results.

```
USER GOAL
  │
COMMANDER ──► PLANNER ──► TASK GRAPH ──► AGENT ROUTER
                                              │
                                              ▼
                                         CODE AGENT
                                              │
                                              ▼
                                       SANDBOX MANAGER
                                              │
                            ┌─────────────────┴─────────────────┐
                            ▼                                   ▼
                    Docker Container                   Isolated Process Sandbox
                     (if available)                   (Strict Jail Sandbox)
                            │                                   │
                            └─────────────────┬─────────────────┘
                                              ▼
                                    LANGUAGE RUNTIME SYSTEM
                                   (Python, JS, C, C++)
                                              │
                                              ▼
                                        EXECUTE & TEST
                                              │
                                              ▼
                                       OBSERVE OUTPUT
                                              │
                                              ▼
                                   DEBUG / RETRY (max 3)
                                              │
                                              ▼
                                        REVIEWER AGENT
                                              │
                                              ▼
                                       DELIVER RESULT
```

## Core Architectural Components
1. **CodeAgent (`backend/app/agents/code_agent.py`)**: Specialist agent operating through Pydantic-validated structured action contracts (`CREATE_FILE`, `UPDATE_FILE`, `COMPILE`, `EXECUTE`, `RUN_TESTS`).
2. **SandboxManager (`backend/app/sandbox/sandbox_manager.py`)**: Manages workspace life cycle, ephemeral sessions, process termination, resource enforcement, and fail-closed safety.
3. **Language Runtime System (`backend/app/sandbox/runtime.py`)**: Pluggable architecture supporting Python, JavaScript, C, and C++.
4. **Filesystem Isolation (`backend/app/sandbox/filesystem.py`)**: Per-execution workspace isolation in `sandbox/{execution_id}/` (`workspace/`, `input/`, `output/`, `artifacts/`).
5. **Network Policy (`backend/app/sandbox/network_policy.py`)**: Default `DENY_ALL` network isolation with IP range enforcement.
