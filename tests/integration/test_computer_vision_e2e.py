import pytest
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.execution_repo import ExecutionRepository
from app.engine.task_graph import TaskGraph, TaskNode
from app.engine.execution_engine import AgentExecutionEngine
from app.perception.perception_engine import PerceptionEngine
from app.computer.computer_manager import computer_manager


@pytest.mark.asyncio
async def test_deterministic_computer_vision_e2e(db_session, monkeypatch):
    from app.config.settings import settings
    monkeypatch.setattr(settings, "COMPUTER_APPROVAL_REQUIRED", False)
    monkeypatch.setattr(settings, "VISION_CONFIDENCE_THRESHOLD", 0.80)


    user_repo = UserRepository(db_session)
    user = await user_repo.create_user("vision_dev", "vision_dev@ultron.ai", "pass12345")

    exec_repo = ExecutionRepository(db_session)
    execution = await exec_repo.create_execution(
        user_id=user.id,
        goal="Perceive local UI application state, detect search input, ground target, type query, click search, and verify perception timeline."
    )

    graph = TaskGraph(execution.id, execution.goal)
    dom_elements = [
        {"id": "input_search", "tag": "input", "label": "search query", "text": "search query", "rect": {"x": 50, "y": 50, "width": 300, "height": 35}, "confidence": 1.0},
        {"id": "btn_search", "tag": "button", "label": "search button", "text": "search button", "rect": {"x": 360, "y": 50, "width": 100, "height": 35}, "confidence": 1.0}
    ]

    t1 = TaskNode("t1", "Capture screen and perceive UI elements", assigned_agent="computer", input_data={"dom_elements": dom_elements})
    t2 = TaskNode("t2", "Type Python IDEs in search query input", assigned_agent="computer", dependencies=["t1"], input_data={"dom_elements": dom_elements, "input_text": "Python IDEs"})
    t3 = TaskNode("t3", "Click search button and verify result", assigned_agent="computer", dependencies=["t2"], input_data={"dom_elements": dom_elements})
    t4 = TaskNode("t4", "Review computer perception and interaction results", assigned_agent="reviewer", dependencies=["t3"])

    for node in [t1, t2, t3, t4]:
        graph.add_task(node)

    engine = AgentExecutionEngine(db_session)
    events = []
    async for evt in engine.run_execution(execution.id, graph, user.id):
        events.append(evt)

    event_types = [e["event_type"] for e in events]
    assert "execution_started" in event_types
    assert "execution_completed" in event_types

    tasks_db = await exec_repo.get_execution_tasks(execution.id)
    assert len(tasks_db) == 4
    for t in tasks_db:
        assert t.status == "COMPLETED"
