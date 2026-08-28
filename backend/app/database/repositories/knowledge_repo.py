import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    KnowledgeWorkspaceModel,
    KnowledgeSourceModel,
    KnowledgeDocumentModel,
    KnowledgeChunkModel,
    KnowledgeEmbeddingModel,
    KnowledgeEntityModel,
    KnowledgeRelationshipModel,
    KnowledgeCitationModel,
    KnowledgeJobModel,
    KnowledgeArtifactModel
)

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Repository enforcing multi-tenant user_id ownership for Phase 8 Knowledge Fabric."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # WORKSPACES
    # -------------------------------------------------------------------------
    async def create_workspace(self, user_id: str, name: str, description: Optional[str] = None, settings: Optional[Dict[str, Any]] = None) -> KnowledgeWorkspaceModel:
        ws = KnowledgeWorkspaceModel(
            user_id=user_id,
            name=name,
            description=description,
            settings_json=settings or {}
        )
        self.db.add(ws)
        await self.db.commit()
        await self.db.refresh(ws)
        return ws

    async def get_workspace(self, workspace_id: str, user_id: str) -> Optional[KnowledgeWorkspaceModel]:
        stmt = select(KnowledgeWorkspaceModel).where(
            KnowledgeWorkspaceModel.id == workspace_id,
            KnowledgeWorkspaceModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_workspaces(self, user_id: str, limit: int = 50, offset: int = 0) -> List[KnowledgeWorkspaceModel]:
        stmt = select(KnowledgeWorkspaceModel).where(
            KnowledgeWorkspaceModel.user_id == user_id
        ).order_by(KnowledgeWorkspaceModel.created_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    # -------------------------------------------------------------------------
    # SOURCES
    # -------------------------------------------------------------------------
    async def create_source(
        self,
        user_id: str,
        workspace_id: str,
        source_type: str,
        filename: str,
        mime_type: str,
        size_bytes: int,
        content_hash: str,
        origin: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeSourceModel:
        src = KnowledgeSourceModel(
            user_id=user_id,
            workspace_id=workspace_id,
            source_type=source_type,
            filename=filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            content_hash=content_hash,
            origin=origin,
            status="PENDING",
            metadata_json=metadata or {}
        )
        self.db.add(src)
        await self.db.commit()
        await self.db.refresh(src)
        return src

    async def get_source(self, source_id: str, user_id: str) -> Optional[KnowledgeSourceModel]:
        stmt = select(KnowledgeSourceModel).where(
            KnowledgeSourceModel.id == source_id,
            KnowledgeSourceModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_source_by_hash(self, content_hash: str, workspace_id: str, user_id: str) -> Optional[KnowledgeSourceModel]:
        stmt = select(KnowledgeSourceModel).where(
            KnowledgeSourceModel.content_hash == content_hash,
            KnowledgeSourceModel.workspace_id == workspace_id,
            KnowledgeSourceModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_sources(self, user_id: str, workspace_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[KnowledgeSourceModel]:
        stmt = select(KnowledgeSourceModel).where(KnowledgeSourceModel.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(KnowledgeSourceModel.workspace_id == workspace_id)
        stmt = stmt.order_by(KnowledgeSourceModel.created_at.desc()).limit(limit).offset(offset)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_source_status(self, source_id: str, user_id: str, status: str) -> Optional[KnowledgeSourceModel]:
        src = await self.get_source(source_id, user_id)
        if src:
            src.status = status
            src.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(src)
        return src

    async def delete_source(self, source_id: str, user_id: str) -> bool:
        stmt = delete(KnowledgeSourceModel).where(
            KnowledgeSourceModel.id == source_id,
            KnowledgeSourceModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount > 0

    # -------------------------------------------------------------------------
    # CHUNKS & EMBEDDINGS
    # -------------------------------------------------------------------------
    async def add_chunk(self, source_id: str, user_id: str, sequence: int, content: str, token_count: int, checksum: str, location: Optional[Dict[str, Any]] = None) -> KnowledgeChunkModel:
        chunk = KnowledgeChunkModel(
            source_id=source_id,
            user_id=user_id,
            sequence=sequence,
            content=content,
            token_count=token_count,
            checksum=checksum,
            location_json=location or {}
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def get_chunks(self, source_id: str, user_id: str) -> List[KnowledgeChunkModel]:
        stmt = select(KnowledgeChunkModel).where(
            KnowledgeChunkModel.source_id == source_id,
            KnowledgeChunkModel.user_id == user_id
        ).order_by(KnowledgeChunkModel.sequence.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def add_embedding(self, chunk_id: str, source_id: str, user_id: str, provider_name: str, model_name: str, dimension: int, vector: List[float]) -> KnowledgeEmbeddingModel:
        emb = KnowledgeEmbeddingModel(
            chunk_id=chunk_id,
            source_id=source_id,
            user_id=user_id,
            provider_name=provider_name,
            model_name=model_name,
            dimension=dimension,
            vector_json=vector
        )
        self.db.add(emb)
        await self.db.commit()
        await self.db.refresh(emb)
        return emb

    # -------------------------------------------------------------------------
    # ENTITIES, RELATIONSHIPS & CITATIONS
    # -------------------------------------------------------------------------
    async def add_entity(self, user_id: str, workspace_id: str, name: str, entity_type: str, confidence: float = 1.0, evidence: Optional[Dict[str, Any]] = None) -> KnowledgeEntityModel:
        ent = KnowledgeEntityModel(
            user_id=user_id,
            workspace_id=workspace_id,
            name=name,
            entity_type=entity_type,
            confidence=confidence,
            evidence_json=evidence or {}
        )
        self.db.add(ent)
        await self.db.commit()
        await self.db.refresh(ent)
        return ent

    async def add_relationship(self, user_id: str, workspace_id: str, source_entity_id: str, target_entity_id: str, relation_type: str, provenance: str, confidence: float = 1.0) -> KnowledgeRelationshipModel:
        rel = KnowledgeRelationshipModel(
            user_id=user_id,
            workspace_id=workspace_id,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relation_type=relation_type,
            provenance=provenance,
            confidence=confidence
        )
        self.db.add(rel)
        await self.db.commit()
        await self.db.refresh(rel)
        return rel

    async def add_citation(self, source_id: str, user_id: str, citation_text: str, location_spec: str) -> KnowledgeCitationModel:
        cit = KnowledgeCitationModel(
            source_id=source_id,
            user_id=user_id,
            citation_text=citation_text,
            location_spec=location_spec
        )
        self.db.add(cit)
        await self.db.commit()
        await self.db.refresh(cit)
        return cit

    async def get_citations(self, source_id: str, user_id: str) -> List[KnowledgeCitationModel]:
        stmt = select(KnowledgeCitationModel).where(
            KnowledgeCitationModel.source_id == source_id,
            KnowledgeCitationModel.user_id == user_id
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
