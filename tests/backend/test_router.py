import pytest
from app.ai.model_manager import ModelManager
from app.engine.router import AgentRouter


def test_agent_router_selection():
    router = AgentRouter(ModelManager())

    assert router.select_agent_for_goal("Write a python script") == "coder"
    assert router.select_agent_for_goal("Research Quantum Computing") == "researcher"
    assert router.select_agent_for_goal("Plan project milestones") == "planner"
    assert router.select_agent_for_goal("Review pull request") == "reviewer"
    assert router.select_agent_for_goal("General query") == "commander"

    assert router.get_agent("coder").__class__.__name__ == "CoderAgent"
    assert router.get_agent("researcher").__class__.__name__ == "ResearcherAgent"
