# PROJECT ULTRON — AGENT CAPABILITY & GOVERNANCE AUDIT

---

## 1. Specialist Agent Governance Matrix

| Agent Name | Allowed Capabilities | Security Boundary & Restrictions | Human Approval Gate |
| :--- | :--- | :--- | :---: |
| **Commander** | Task decomposition, DAG plan creation | Cannot directly execute shell or database mutations | No |
| **Planner** | Task dependency resolution | Constrained to DAG node graph generation | No |
| **Researcher** | Web search, page fetching | Playwright Chromium sandbox, SSRF private IP blocked | No |
| **Coder** | Python/C/C++/JS generation & execution | Sandboxed process jail, 30s timeout, path traversal block | No (Safe Code) |
| **Reviewer** | Execution output validation | Read-only analysis of task outputs | No |
| **BrowserAgent** | Web interaction, form typing | Domain policy filter, sensitive action approval gate | Yes (Form Submit) |
| **ComputerAgent** | Screen grounding, click/type | Viewport coordinate validation, low confidence rejection | Yes (Visual Writes) |
| **LearningAgent** | Strategy optimization, memory extraction | Secret detector strips credentials before save | No |
| **KnowledgeAgent** | Multi-format ingestion, hybrid search | Executable signature validation, XML content wrapping | No |
| **AutonomyAgent** | Scheduled rule execution | Cooldown windows, EventBus deduplication | Yes (Level 3+) |
| **IntegrationAgent** | GitHub, Calendar, Email ops | Scope risk classification, AES-256 encrypted tokens | Yes (Mutations) |

---

## 2. Unified Security Gate Enforcement

No specialist agent is permitted to bypass the **Unified Security Gate**. Sensitive mutations (sending email, merging PRs, scheduling events, executing Level 3 autonomy actions) strictly require **human approval (`WAITING_FOR_APPROVAL`)** before execution.
