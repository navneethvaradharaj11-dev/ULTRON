import pytest
from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.memory_retriever import MemoryRetriever
from app.intelligence.embedding_provider import MockEmbeddingProvider

@pytest.mark.asyncio
async def test_memory_retrieval_and_ranking(db_session):
    engine = MemoryEngine(db_session, MockEmbeddingProvider())
    await engine.add_memory("user_1", "FastAPI backend architecture with MySQL", "SEMANTIC", importance=5)
    await engine.add_memory("user_1", "Flutter mobile app for dashboard UI", "SEMANTIC", importance=3)
    await engine.add_memory("user_1", "Unrelated memory about cooking recipes", "SEMANTIC", importance=1)

    retriever = MemoryRetriever(db_session, engine)
    retrieved = await retriever.retrieve_relevant_memories(
        user_id="user_1",
        user_request="How do we configure FastAPI and MySQL?",
        top_k=2
    )

    assert len(retrieved) == 2
    assert "FastAPI" in retrieved[0]["content"]
    assert retrieved[0]["score"] >= retrieved[1]["score"]
