import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.intelligence.embedding_provider import EmbeddingProvider, MockEmbeddingProvider
from app.database.repositories.knowledge_repo import KnowledgeRepository

logger = logging.getLogger("ULTRON.EmbeddingIndex")


class EmbeddingIndex:
    """Manages generation and storage of vector embeddings for Knowledge Fabric chunks."""

    def __init__(self, db: AsyncSession, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()

    async def index_chunk(self, chunk_id: str, source_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """Generate and store embedding vector for chunk."""
        vector = await self.embedding_provider.embed_text(content)
        provider_name = self.embedding_provider.get_provider_name()
        dimension = self.embedding_provider.get_dimension()

        emb_model = await self.repo.add_embedding(
            chunk_id=chunk_id,
            source_id=source_id,
            user_id=user_id,
            provider_name=provider_name,
            model_name="default",
            dimension=dimension,
            vector=vector
        )

        return {
            "embedding_id": emb_model.id,
            "chunk_id": chunk_id,
            "provider": provider_name,
            "dimension": dimension
        }
