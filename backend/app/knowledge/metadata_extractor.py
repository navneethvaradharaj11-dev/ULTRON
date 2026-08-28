import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ULTRON.MetadataExtractor")


class MetadataExtractor:
    """Extracts structural metadata, file properties, and document attributes."""

    @staticmethod
    def extract_metadata(filename: str, mime_type: str, size_bytes: int, origin: str) -> Dict[str, Any]:
        return {
            "filename": filename,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "origin": origin,
            "category": MetadataExtractor._determine_category(mime_type, filename)
        }

    @staticmethod
    def _determine_category(mime_type: str, filename: str) -> str:
        if "pdf" in mime_type or filename.endswith(".pdf"):
            return "DOCUMENT"
        elif "word" in mime_type or filename.endswith(".docx"):
            return "DOCUMENT"
        elif "excel" in mime_type or "csv" in mime_type or filename.endswith((".xlsx", ".csv")):
            return "SPREADSHEET"
        elif "presentation" in mime_type or filename.endswith(".pptx"):
            return "PRESENTATION"
        elif "image" in mime_type:
            return "IMAGE"
        elif "audio" in mime_type:
            return "AUDIO"
        elif "video" in mime_type:
            return "VIDEO"
        else:
            return "GENERAL"
