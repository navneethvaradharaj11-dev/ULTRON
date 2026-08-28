import os
import hashlib
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("ULTRON.ArtifactManager")


class ArtifactManager:
    """Unified artifact lifecycle manager (CREATED, VALIDATED, READY, EXPORTED, ARCHIVED, DELETED)."""

    @staticmethod
    def create_artifact_record(
        user_id: str,
        filename: str,
        file_path: str,
        artifact_type: str,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        checksum = ""
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

        return {
            "artifact_id": f"art_{hashlib.md5(file_path.encode()).hexdigest()[:12]}",
            "user_id": user_id,
            "workflow_id": workflow_id,
            "filename": filename,
            "file_path": file_path,
            "artifact_type": artifact_type,
            "size_bytes": size,
            "checksum": checksum,
            "status": "READY",
            "created_at": datetime.utcnow().isoformat()
        }
