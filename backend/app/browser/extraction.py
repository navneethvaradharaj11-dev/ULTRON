import uuid
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from datetime import datetime


class StructuredExtractor:
    """Formatter and extractor for structured browser observations and source tracking."""

    @classmethod
    def format_source_metadata(
        cls,
        url: str,
        title: str,
        summary: str,
        source_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create structured research source tracking record."""
        domain = urlparse(url).netloc or "unknown"
        sid = source_id or f"src_{uuid.uuid4().hex[:8]}"

        return {
            "source_id": sid,
            "url": url,
            "title": title or "Untitled Source",
            "domain": domain,
            "retrieved_at": datetime.utcnow().isoformat(),
            "content_summary": summary[:500] if summary else ""
        }

    @classmethod
    def create_structured_fact_extraction(
        cls,
        source_url: str,
        facts: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Build structured fact extraction schema."""
        formatted_facts = []
        for f in facts:
            formatted_facts.append({
                "field": str(f.get("field", "information")),
                "value": str(f.get("value", "")),
                "evidence": str(f.get("evidence", ""))
            })

        return {
            "source": source_url,
            "facts": formatted_facts,
            "extracted_at": datetime.utcnow().isoformat()
        }
