import pytest
from app.intelligence.agent_metrics import AgentMetricsEngine

@pytest.mark.asyncio
async def test_intelligence_agent_metrics_tracking(db_session):
    engine = AgentMetricsEngine(db_session)
    await engine.record_agent_run(
        agent_name="researcher",
        success=True,
        duration_ms=800,
        retries=0,
        tools_used=["web_search"],
        review_score=1.0
    )

    metrics = await engine.get_all_metrics()
    assert len(metrics) >= 8
    
    researcher = next(m for m in metrics if m["agent_name"] == "researcher")
    assert researcher["total_runs"] == 1
    assert researcher["successful_runs"] == 1
    assert researcher["success_rate"] == 1.0
