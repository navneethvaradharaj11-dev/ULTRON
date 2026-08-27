# MySQL Database Schema Documentation

ULTRON uses MySQL as its primary relational database.

## Table Inventory
1. **users**: User identity, username, email, password hashes.
2. **sessions**: User active JWT session hashes and expiration.
3. **conversations**: Chat conversation containers per user.
4. **messages**: Individual conversation messages with sender metadata.
5. **memories**: Long-term facts and preference store with importance scores.
6. **tasks**: Task management items created by users or agents.
7. **agents**: Registered ULTRON agent models (`commander`, `planner`, `researcher`, `coder`, `reviewer`).
8. **agent_runs**: Audit logs of agent workflow executions, prompts, and timing.
9. **tool_calls**: Audit logs of tool invocations, parameters, approval statuses, and results.
10. **permissions**: Per-user tool execution permission overrides (`allow`, `deny`, `require_approval`).
11. **audit_logs**: Security action log entries.
