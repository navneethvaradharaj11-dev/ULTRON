import pytest
from app.intelligence.strategy_engine import StrategyEngine

@pytest.mark.asyncio
async def test_strategy_engine_record_and_retrieve(db_session):
    engine = StrategyEngine(db_session)
    await engine.record_strategy_execution(
        goal_type="research_and_compare",
        description="Search web and compare findings",
        steps=[{"step": 1, "action": "search"}],
        agents=["researcher", "reviewer"],
        tools=["web_search"],
        success=True,
        duration_ms=1200
    )

    best = await engine.best_strategy("research_and_compare")
    assert best is not None
    assert best["goal_type"] == "research_and_compare"
    assert best["success_rate"] == 1.0
