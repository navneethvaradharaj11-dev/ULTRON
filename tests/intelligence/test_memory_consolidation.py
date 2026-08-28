import pytest
from app.intelligence.memory_consolidator import MemoryConsolidator

@pytest.mark.asyncio
async def test_consolidation_combines_observations(db_session):
    consolidator = MemoryConsolidator(db_session)
    observations = [
        {"topic": "Tech Stack", "fact": "Python"},
        {"topic": "Tech Stack", "fact": "FastAPI"},
        {"topic": "Tech Stack", "fact": "Flutter"},
        {"topic": "Tech Stack", "fact": "MySQL"},
    ]

    res = await consolidator.consolidate_observations(
        user_id="user_c",
        observations=observations,
        category="SEMANTIC"
    )

    assert res["status"] == "SUCCESS"
    assert res["consolidated_count"] == 1
