# Initial Seed Data for ULTRON Agents

INITIAL_AGENTS = [
    {
        "id": "agent-commander-001",
        "name": "Commander Agent",
        "code_name": "commander",
        "description": "Understands user intent, coordinates multi-agent execution strategy, and returns final results.",
        "capabilities_json": ["intent_understanding", "delegation", "orchestration"],
        "status": "active"
    },
    {
        "id": "agent-planner-002",
        "name": "Planner Agent",
        "code_name": "planner",
        "description": "Decomposes complex requests into structured, executable step-by-step task plans.",
        "capabilities_json": ["task_decomposition", "workflow_planning"],
        "status": "active"
    },
    {
        "id": "agent-researcher-003",
        "name": "Researcher Agent",
        "code_name": "researcher",
        "description": "Gathers information from tools, web search, memory, and documentation.",
        "capabilities_json": ["web_search", "memory_query", "information_retrieval"],
        "status": "active"
    },
    {
        "id": "agent-coder-004",
        "name": "Coding Agent",
        "code_name": "coder",
        "description": "Generates code snippets, evaluates filesystem scripts, and solves technical programming tasks.",
        "capabilities_json": ["code_generation", "code_review", "filesystem_operations"],
        "status": "active"
    },
    {
        "id": "agent-reviewer-005",
        "name": "Reviewer Agent",
        "code_name": "reviewer",
        "description": "Evaluates agent outputs, checks tool parameters against security policies, and validates results.",
        "capabilities_json": ["validation", "safety_checking", "quality_assessment"],
        "status": "active"
    }
]
