import pytest
from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.embedding_provider import MockEmbeddingProvider

@pytest.mark.asyncio
async def test_add_and_get_memory(db_session):
    engine = MemoryEngine(db_session, MockEmbeddingProvider())
    mem = await engine.add_memory(
        user_id="test_user_id",
        content="User prefers Python for data processing",
        memory_type="PREFERENCE",
        importance=4,
        confidence=0.95
    )

    assert mem["id"] is not None
    assert mem["type"] == "PREFERENCE"
    assert mem["content"] == "User prefers Python for data processing"

    fetched = await engine.get_memory(mem["id"], user_id="test_user_id")
    assert fetched is not None
    assert fetched["access_count"] == 1


@pytest.mark.asyncio
async def test_cross_user_memory_isolation(db_session):
    engine = MemoryEngine(db_session, MockEmbeddingProvider())
    mem = await engine.add_memory(
        user_id="user_a",
        content="Private memory for User A",
        memory_type="SEMANTIC"
    )

    # User B attempting to access User A's memory must fail (return None)
    fetched = await engine.get_memory(mem["id"], user_id="user_b")
    assert fetched is None
