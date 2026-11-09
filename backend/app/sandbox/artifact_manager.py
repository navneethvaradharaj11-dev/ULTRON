import os
import hashlib
import mimetypes
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ULTRON.ArtifactManager")


class ArtifactManager:
    """Manages creation, hashing, and registration of execution artifacts."""

    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

    def create_artifact(self, filename: str, content_bytes: bytes, mime_type: Optional[str] = None) -> Dict[str, Any]:
        """Save artifact file to disk and compute hash and metadata."""
        dest_path = os.path.join(self.artifacts_dir, filename)
        with open(dest_path, "wb") as f:
            f.write(content_bytes)

        sha256_hash = hashlib.sha256(content_bytes).hexdigest()
        detected_mime, _ = mimetypes.guess_type(filename)

        return {
            "filename": filename,
            "sandbox_path": dest_path,
            "mime_type": mime_type or detected_mime or "application/octet-stream",
            "size_bytes": len(content_bytes),
            "hash_sha256": sha256_hash
        }
