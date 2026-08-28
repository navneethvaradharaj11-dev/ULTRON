import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.knowledge_repo import KnowledgeRepository
from app.knowledge.document_parser import DocumentParser
from app.knowledge.audio_parser import AudioParser
from app.knowledge.video_parser import VideoParser
from app.knowledge.chunker import StructureAwareChunker
from app.knowledge.embedding_index import EmbeddingIndex
from app.knowledge.entity_extractor import EntityExtractor
from app.knowledge.relationship_engine import RelationshipEngine
from app.knowledge.knowledge_security import KnowledgeSecurity

logger = logging.getLogger("ULTRON.IngestionEngine")


class IngestionEngine:
    """Ingestion Engine parsing documents, chunking content, generating embeddings, and extracting entities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = KnowledgeRepository(db)
        self.embedding_index = EmbeddingIndex(db)

    async def process_source(self, source_id: str, user_id: str) -> Dict[str, Any]:
        """Ingest source through full processing pipeline."""
        src = await self.repo.get_source(source_id, user_id)
        if not src:
            raise ValueError(f"Knowledge source '{source_id}' not found for user '{user_id}'")

        await self.repo.update_source_status(source_id, user_id, "PROCESSING")

        filepath = src.metadata_json.get("storage_path") if src.metadata_json else None
        if not filepath or not os.path.exists(filepath):
            await self.repo.update_source_status(source_id, user_id, "FAILED")
            raise ValueError(f"Storage file missing for source '{source_id}'")

        # 1. Parsing
        stype = src.source_type.upper()
        raw_text = ""
        sections = []

        if stype == "AUDIO":
            p_audio = AudioParser.parse_audio(filepath, src.filename)
            raw_text = p_audio.full_transcript
            sections = p_audio.segments
        elif stype == "VIDEO":
            p_vid = VideoParser.parse_video(filepath, src.filename)
            raw_text = p_vid.full_description
            sections = p_vid.frames
        else:
            parsed_doc = DocumentParser.parse_document(filepath, src.filename)
            raw_text = parsed_doc.raw_text
            sections = parsed_doc.sections

        # 2. Chunking
        chunks = StructureAwareChunker.chunk_parsed_sections(source_id, sections)

        # Save Chunks & Embeddings
        indexed_chunks = []
        for chk in chunks:
            # Wrap in untrusted boundaries to prevent injection
            safe_text = KnowledgeSecurity.wrap_untrusted_content(chk.content, src.filename)
            db_chk = await self.repo.add_chunk(
                source_id=source_id,
                user_id=user_id,
                sequence=chk.sequence,
                content=safe_text,
                token_count=chk.token_count,
                checksum=chk.checksum,
                location={"location": chk.location_spec}
            )

            emb = await self.embedding_index.index_chunk(
                chunk_id=db_chk.id,
                source_id=source_id,
                user_id=user_id,
                content=chk.content
            )
            indexed_chunks.append(db_chk.id)

        # 3. Entity & Relationship Extraction
        entities = EntityExtractor.extract_entities(raw_text)
        db_entities = []
        for ent in entities:
            e_model = await self.repo.add_entity(
                user_id=user_id,
                workspace_id=src.workspace_id,
                name=ent["name"],
                entity_type=ent["entity_type"],
                confidence=ent["confidence"],
                evidence={"evidence": ent["evidence"]}
            )
            db_entities.append(e_model)

        relationships = RelationshipEngine.infer_relationships(entities, src.filename)
        for rel in relationships:
            await self.repo.add_relationship(
                user_id=user_id,
                workspace_id=src.workspace_id,
                source_entity_id=db_entities[0].id if db_entities else "ent_1",
                target_entity_id=db_entities[1].id if len(db_entities) > 1 else "ent_2",
                relation_type=rel["relation_type"],
                provenance=rel["provenance"],
                confidence=rel["confidence"]
            )

        # Mark Status COMPLETED
        await self.repo.update_source_status(source_id, user_id, "COMPLETED")

        return {
            "source_id": source_id,
            "status": "COMPLETED",
            "chunks_created": len(indexed_chunks),
            "entities_extracted": len(entities),
            "relationships_created": len(relationships)
        }
