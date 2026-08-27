# ULTRON Agent Architecture Documentation

ULTRON employs a multi-agent modular architecture.

## Agents & Roles
- **Commander Agent**: Master intent parser and work orchestrator.
- **Planner Agent**: Task decomposition engine converting goals into executable sub-task plans.
- **Researcher Agent**: Information gathering and search synthesis agent.
- **Coding Agent**: Code snippet generation and syntax reviewer.
- **Reviewer Agent**: Quality assurance, parameter validation, and output security reviewer.

## Execution Lifecycle
1. User prompt received via REST or WebSocket.
2. Context window constructed from message history and long-term memory.
3. Commander Agent assesses intent and delegates to Planner or Tool Registry.
4. Agent runs (`agent_runs`) and tool executions (`tool_calls`) logged to MySQL database.
5. Structured events streamed via WebSocket protocol to UI.
