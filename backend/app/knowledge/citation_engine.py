import logging
from typing import List, Dict, Any

logger = logging.getLogger("ULTRON.CitationEngine")


class CitationEngine:
    """Formats traceable, provenance-backed citations for knowledge results."""

    @staticmethod
    def format_citation(index: int, filename: str, location_spec: str) -> str:
        """Format citation string: [index] filename — location_spec."""
        loc = location_spec or "Document"
        return f"[{index}] {filename} — {loc}"

    @staticmethod
    def generate_evidence_package(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build structured evidence package containing citations and untrusted content blocks."""
        citations = []
        evidence_blocks = []

        for idx, res in enumerate(results, 1):
            cit_str = CitationEngine.format_citation(
                index=idx,
                filename=res.get("filename", "unknown"),
                location_spec=res.get("location_spec", "Document")
            )
            citations.append(cit_str)
            evidence_blocks.append({
                "citation": cit_str,
                "filename": res.get("filename"),
                "content": res.get("content"),
                "score": res.get("final_score", res.get("score", 0.0))
            })

        return {
            "citations": citations,
            "evidence": evidence_blocks,
            "source_count": len(evidence_blocks)
        }
