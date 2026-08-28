import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.intelligence.memory_engine import MemoryEngine
from app.knowledge.knowledge_engine import KnowledgeEngine

logger = logging.getLogger("ULTRON.PersonalContextEngine")


class PersonalContextEngine:
    """Personal Context Engine providing scoped context retrieval without prompt pollution."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.memory_engine = MemoryEngine(db)
        self.knowledge_engine = KnowledgeEngine(db)

    async def build_scoped_context(
        self,
        user_id: str,
        goal: str,
        workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # 1. Retrieve relevant durable memories
        memories = await self.memory_engine.retrieve_memories(user_id, goal, limit=3)
        formatted_memories = [m.get("content", "") for m in memories]

        # 2. Retrieve knowledge context if workspace specified
        knowledge_chunks = []
        if workspace_id:
            k_res = await self.knowledge_engine.query_knowledge(user_id, goal, workspace_id, top_k=3)
            knowledge_chunks = [r.get("text", "") for r in k_res.get("results", [])]

        return {
            "user_id": user_id,
            "goal": goal,
            "user_memories": formatted_memories,
            "knowledge_chunks": knowledge_chunks,
            "has_context": len(formatted_memories) > 0 or len(knowledge_chunks) > 0
        }
