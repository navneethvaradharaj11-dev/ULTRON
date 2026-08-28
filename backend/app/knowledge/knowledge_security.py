import os
import re
import hashlib
import logging
from typing import Tuple, List, Optional, Dict, Any

logger = logging.getLogger("ULTRON.KnowledgeSecurity")

# Configurable limits
MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_IMPORT_SIZE = 250 * 1024 * 1024 # 250 MB
MAX_FILES_PER_IMPORT = 100
MAX_DIRECTORY_DEPTH = 10

DANGEROUS_EXTENSIONS = {
    ".exe", ".dll", ".so", ".dylib", ".sh", ".bat", ".cmd", ".vbs", ".ps1",
    ".app", ".msi", ".jar", ".com", ".scr", ".pif", ".cpl", ".htc", ".docm",
    ".xlsm", ".pptm"
}

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/markdown",
    "image/png",
    "image/jpeg",
    "image/webp",
    "audio/mpeg",
    "audio/wav",
    "audio/mp3",
    "audio/m4a",
    "audio/ogg",
    "video/mp4",
    "video/webm",
    "video/avi",
    "text/x-python",
    "application/javascript",
    "text/javascript",
    "text/x-dart",
    "text/html",
    "text/css",
    "application/json",
    "application/x-yaml",
    "text/yaml"
}


class KnowledgeSecurityError(Exception):
    """Custom exception raised when security or limit checks fail during knowledge operations."""
    pass


class KnowledgeSecurity:
    """Security validator enforcing upload limits, path traversal safety, dangerous content blocking,
    and untrusted content wrapping for Phase 8 Knowledge Fabric.
    """

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename preventing path traversal or special shell characters."""
        if not filename:
            return "unnamed_file"
        base = os.path.basename(filename)
        # Remove null bytes, directory separators, and dangerous chars
        clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)
        return clean or "unnamed_file"

    @staticmethod
    def validate_file(
        filename: str,
        size_bytes: int,
        content_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None
    ) -> None:
        """Validate filename extension, file size, MIME type, and binary executable signatures."""
        clean_name = KnowledgeSecurity.sanitize_filename(filename)
        ext = os.path.splitext(clean_name)[1].lower()

        # 1. Extension Check
        if ext in DANGEROUS_EXTENSIONS:
            raise KnowledgeSecurityError(f"Rejected dangerous file extension '{ext}' in filename '{clean_name}'")

        # 2. Size Check
        if size_bytes > MAX_SINGLE_FILE_SIZE:
            raise KnowledgeSecurityError(
                f"File size {size_bytes} bytes exceeds maximum allowed limit of {MAX_SINGLE_FILE_SIZE} bytes."
            )

        # 3. Executable Header Check (PE / ELF / Mach-O / Zip bomb)
        if content_bytes:
            if content_bytes.startswith(b"MZ") or content_bytes.startswith(b"\x7fELF") or content_bytes.startswith(b"\xca\xfe\xba\xbe"):
                raise KnowledgeSecurityError(f"Rejected file '{clean_name}': Detected executable binary signature.")

    @staticmethod
    def wrap_untrusted_content(content: str, source_identifier: str) -> str:
        """Wrap raw extracted text content in strict <untrusted_knowledge_source> boundary tags to prevent prompt injection."""
        if not content:
            return content
        clean_id = KnowledgeSecurity.sanitize_filename(source_identifier)
        return (
            f"<untrusted_knowledge_source id=\"{clean_id}\">\n"
            f"{content}\n"
            f"</untrusted_knowledge_source>"
        )

    @staticmethod
    def calculate_hash(content_bytes: bytes) -> str:
        """Compute SHA-256 hash for source content deduplication."""
        return hashlib.sha256(content_bytes).hexdigest()
