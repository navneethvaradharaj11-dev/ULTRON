import hashlib
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("ULTRON.StructureAwareChunker")


class KnowledgeChunk(BaseModel):
    chunk_id: str
    source_id: str
    sequence: int
    content: str
    token_count: int
    location_spec: str
    checksum: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StructureAwareChunker:
    """Intelligent structure-aware chunker breaking content into semantic chunks with location specs."""

    @staticmethod
    def chunk_parsed_sections(
        source_id: str,
        sections: List[Any],
        max_tokens_per_chunk: int = 500
    ) -> List[KnowledgeChunk]:
        chunks: List[KnowledgeChunk] = []
        sequence = 0

        for sec in sections:
            content = getattr(sec, "content", str(sec)).strip()
            if not content:
                continue

            loc_spec = getattr(sec, "location_spec", "Document")
            sec_title = getattr(sec, "title", "")

            # Split large content into sub-chunks if necessary
            words = content.split()
            chunk_size_words = max_tokens_per_chunk // 2  # Approx 2 words per token

            if len(words) <= chunk_size_words:
                sub_chunks = [content]
            else:
                sub_chunks = [
                    " ".join(words[i:i + chunk_size_words])
                    for i in range(0, len(words), chunk_size_words)
                ]

            for sub_text in sub_chunks:
                sequence += 1
                chunk_id = f"{source_id}_chunk_{sequence}"
                chk_sum = hashlib.sha256(sub_text.encode("utf-8")).hexdigest()
                tok_cnt = len(sub_text.split())

                chunks.append(KnowledgeChunk(
                    chunk_id=chunk_id,
                    source_id=source_id,
                    sequence=sequence,
                    content=sub_text,
                    token_count=tok_cnt,
                    location_spec=loc_spec,
                    checksum=chk_sum,
                    metadata={"section_title": sec_title, "location": loc_spec}
                ))

        return chunks
