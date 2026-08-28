import pytest
from app.knowledge.document_parser import ParsedSection
from app.knowledge.chunker import StructureAwareChunker


def test_structure_aware_chunking():
    sections = [
        ParsedSection(title="Section 1", content="Paragraph 1 about CPU scheduling.", location_spec="Page 1"),
        ParsedSection(title="Section 2", content="Paragraph 2 about Round Robin algorithm.", location_spec="Page 2")
    ]

    chunks = StructureAwareChunker.chunk_parsed_sections("src_123", sections)
    assert len(chunks) == 2
    assert chunks[0].location_spec == "Page 1"
    assert chunks[1].location_spec == "Page 2"
    assert chunks[0].checksum != ""
