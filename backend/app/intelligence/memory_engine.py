import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.intelligence_repo import IntelligenceRepository
from app.intelligence.secret_detector import SecretDetector
from app.intelligence.embedding_provider import EmbeddingProvider, MockEmbeddingProvider
from app.database.models import Memory, MemoryEmbeddingModel

logger = logging.getLogger("ULTRON.MemoryEngine")

VALID_MEMORY_TYPES = {"WORKING", "EPISODIC", "SEMANTIC", "PROCEDURAL", "PREFERENCE"}


class MemoryEngine:
    """Central Memory Engine orchestrating standard CRUD, secret safety,
    multi-tenant isolation, and vector embedding generation.
    """

    def __init__(self, db: AsyncSession, embedding_provider: Optional[EmbeddingProvider] = None):
        self.db = db
        self.repo = IntelligenceRepository(db)
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()

    async def add_memory(
        self,
        user_id: str,
        content: str,
        memory_type: str = "SEMANTIC",
        importance: int = 1,
        confidence: float = 1.0,
        source: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
        auto_sanitize: bool = True
    ) -> Dict[str, Any]:
        """Create and store memory with secret protection and optional vector embeddings."""
        m_type = memory_type.upper()
        if m_type not in VALID_MEMORY_TYPES:
            raise ValueError(f"Invalid memory type '{memory_type}'. Allowed: {VALID_MEMORY_TYPES}")

        if not user_id:
            raise ValueError("user_id is required for multi-tenant memory ownership.")

        has_secret, secret_types = SecretDetector.contains_secret(content)
        if has_secret:
            if auto_sanitize:
                content = SecretDetector.sanitize(content)
                logger.warning("Sanitized sensitive secret (%s) from memory for user '%s'", secret_types, user_id)
            else:
                raise ValueError(f"Refusing to store memory containing sensitive secret: {secret_types}")

        mem = await self.repo.create_memory(
            user_id=user_id,
            content=content,
            memory_type=m_type,
            importance=importance,
            confidence=confidence,
            source=source,
            metadata=metadata
        )

        # Generate vector embedding if provider available
        if self.embedding_provider:
            try:
                vector = await self.embedding_provider.embed_text(mem.content)
                embed_model = MemoryEmbeddingModel(
                    memory_id=mem.id,
                    vector_json=vector,
                    dimension=self.embedding_provider.get_dimension(),
                    provider_name=self.embedding_provider.get_provider_name()
                )
                self.db.add(embed_model)
                await self.db.commit()
            except Exception as e:
                logger.warning("Embedding generation notice for memory '%s': %s (Memory saved without embedding)", mem.id, e)

        return self.to_dict(mem)

    async def get_memory(self, memory_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        mem = await self.repo.get_memory_by_id(memory_id, user_id=user_id)
        if not mem:
            return None
        await self.repo.touch_memory(mem.id)
        return self.to_dict(mem)

    async def list_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        mems = await self.repo.get_user_memories(user_id=user_id, memory_type=memory_type, limit=limit)
        return [self.to_dict(m) for m in mems]

    async def update_memory(
        self,
        memory_id: str,
        user_id: str,
        content: Optional[str] = None,
        importance: Optional[int] = None,
        confidence: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if content:
            has_secret, secret_types = SecretDetector.contains_secret(content)
            if has_secret:
                content = SecretDetector.sanitize(content)

        mem = await self.repo.update_memory(
            memory_id=memory_id,
            user_id=user_id,
            content=content,
            importance=importance,
            confidence=confidence,
            reason=reason
        )
        if not mem:
            return None
        return self.to_dict(mem)

    async def forget_memory(self, memory_id: str, user_id: str) -> bool:
        return await self.repo.forget_memory(memory_id=memory_id, user_id=user_id)

    async def delete_memory(self, memory_id: str, user_id: str) -> bool:
        return await self.repo.delete_memory(memory_id=memory_id, user_id=user_id)

    async def retrieve_memories(self, user_id: str, query: str = "", limit: int = 10) -> List[Dict[str, Any]]:
        from app.intelligence.memory_retriever import MemoryRetriever
        retriever = MemoryRetriever(self.db)
        return await retriever.retrieve_relevant_memories(user_id=user_id, user_request=query, top_k=limit)


    @staticmethod
    def to_dict(mem: Memory) -> Dict[str, Any]:
        return {
            "id": mem.id,
            "user_id": mem.user_id,
            "type": mem.memory_type,
            "content": mem.content,
            "importance": mem.importance,
            "confidence": mem.confidence,
            "source": mem.source,
            "created_at": mem.created_at.isoformat() if mem.created_at else None,
            "updated_at": mem.updated_at.isoformat() if mem.updated_at else None,
            "last_accessed": mem.last_accessed.isoformat() if mem.last_accessed else None,
            "access_count": mem.access_count,
            "status": mem.status,
            "metadata": mem.metadata_json or {}
        }
