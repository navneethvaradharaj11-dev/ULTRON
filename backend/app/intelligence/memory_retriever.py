import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.memory_engine import MemoryEngine
from app.intelligence.memory_ranker import MemoryRanker

logger = logging.getLogger("ULTRON.MemoryRetriever")


class MemoryRetriever:
    """Intelligent multi-stage memory retriever."""

    def __init__(self, db: AsyncSession, memory_engine: Optional[MemoryEngine] = None):
        self.db = db
        self.memory_engine = memory_engine or MemoryEngine(db)

    async def retrieve_relevant_memories(
        self,
        user_id: str,
        user_request: str,
        top_k: int = 5,
        memory_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query generation -> Candidate retrieval -> Ranking pipeline."""
        if not user_id:
            raise ValueError("user_id is required for memory retrieval.")

        # Candidate retrieval scoped strictly to user_id
        candidates = await self.memory_engine.list_memories(
            user_id=user_id,
            memory_type=memory_type,
            limit=50
        )

        if not candidates:
            return []

        # Rank candidates using multi-factor scoring
        ranked = MemoryRanker.rank_candidates(candidates, user_request, top_k=top_k)
        
        # Touch retrieved memories
        for r in ranked:
            await self.memory_engine.repo.touch_memory(r["id"])

        return ranked

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Exact/keyword memory search with tenant isolation."""
        candidates = await self.memory_engine.list_memories(user_id=user_id, limit=100)
        return MemoryRanker.rank_candidates(candidates, query, top_k=limit)
