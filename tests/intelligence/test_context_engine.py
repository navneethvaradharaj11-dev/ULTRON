from app.intelligence.context_engine import ContextEngine

def test_context_engine_formatting():
    ctx = ContextEngine.build_context(
        user_request="Build FastAPI backend endpoint",
        retrieved_memories=[{"type": "SEMANTIC", "content": "Use SQLAlchemy ORM"}],
        preferences=[{"key": "editor", "value": "vscode"}],
        execution_state={"status": "RUNNING", "tasks_completed": 1, "total_tasks": 2}
    )

    assert "### CURRENT_TASK" in ctx
    assert "### RELEVANT_MEMORIES" in ctx
    assert "### KNOWN_PREFERENCES" in ctx
    assert "### CURRENT_EXECUTION_STATE" in ctx
    assert "Use SQLAlchemy ORM" in ctx
