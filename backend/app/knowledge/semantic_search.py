import math
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import KnowledgeEmbeddingModel, KnowledgeChunkModel, KnowledgeSourceModel
from app.intelligence.embedding_provider import EmbeddingProvider, MockEmbeddingProvider

logger = logging.getLogger("ULTRON.SemanticSearch")


class SemanticSearch:
    """Performs vector similarity search over tenant-isolated knowledge embeddings."""

    def __init__(self, db: AsyncSession, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db = db
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    async def search(self, user_id: str, query: str, workspace_id: Optional[str] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        query_vector = await self.embedding_provider.embed_text(query)

        stmt = select(
            KnowledgeEmbeddingModel,
            KnowledgeChunkModel,
            KnowledgeSourceModel
        ).join(
            KnowledgeChunkModel, KnowledgeEmbeddingModel.chunk_id == KnowledgeChunkModel.id
        ).join(
            KnowledgeSourceModel, KnowledgeChunkModel.source_id == KnowledgeSourceModel.id
        ).where(
            KnowledgeEmbeddingModel.user_id == user_id
        )

        if workspace_id:
            stmt = stmt.where(KnowledgeSourceModel.workspace_id == workspace_id)

        res = await self.db.execute(stmt)
        rows = res.all()

        scored_results = []
        for emb, chunk, source in rows:
            vec = emb.vector_json or []
            sim = self.cosine_similarity(query_vector, vec)
            scored_results.append({
                "chunk_id": chunk.id,
                "source_id": source.id,
                "filename": source.filename,
                "content": chunk.content,
                "location_spec": chunk.location_json.get("location", "Document") if chunk.location_json else "Document",
                "similarity": sim,
                "score": sim
            })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]
