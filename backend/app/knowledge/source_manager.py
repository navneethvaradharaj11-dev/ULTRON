import os
import shutil
import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.knowledge_repo import KnowledgeRepository
from app.knowledge.knowledge_security import KnowledgeSecurity, KnowledgeSecurityError

logger = logging.getLogger("ULTRON.SourceManager")

BASE_SANDBOX_DIR = "sandbox/knowledge"


class SourceManager:
    """Manages file storage, path isolation, content deduplication, and workspace lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = KnowledgeRepository(db)

    @staticmethod
    def get_workspace_dir(user_id: str, workspace_id: str) -> str:
        clean_user = KnowledgeSecurity.sanitize_filename(user_id)
        clean_ws = KnowledgeSecurity.sanitize_filename(workspace_id)
        path = os.path.join(BASE_SANDBOX_DIR, clean_user, clean_ws)
        os.makedirs(os.path.join(path, "originals"), exist_ok=True)
        os.makedirs(os.path.join(path, "extracted"), exist_ok=True)
        os.makedirs(os.path.join(path, "chunks"), exist_ok=True)
        os.makedirs(os.path.join(path, "artifacts"), exist_ok=True)
        return path

    async def register_source_file(
        self,
        user_id: str,
        workspace_id: str,
        filename: str,
        content_bytes: bytes,
        mime_type: str,
        origin: str = "upload"
    ) -> Tuple[Any, bool]:
        """Save file in tenant sandbox, perform content hash deduplication."""
        size_bytes = len(content_bytes)
        KnowledgeSecurity.validate_file(filename, size_bytes, content_bytes, mime_type)

        content_hash = KnowledgeSecurity.calculate_hash(content_bytes)

        # Check for existing duplicate file in workspace
        existing = await self.repo.get_source_by_hash(content_hash, workspace_id, user_id)
        if existing:
            logger.info("Source deduplication: Source with hash '%s' already exists in workspace '%s'", content_hash, workspace_id)
            return existing, True

        ws_dir = self.get_workspace_dir(user_id, workspace_id)
        clean_fn = KnowledgeSecurity.sanitize_filename(filename)
        save_path = os.path.join(ws_dir, "originals", f"{content_hash}_{clean_fn}")

        with open(save_path, "wb") as f:
            f.write(content_bytes)

        source_type = self._determine_type(clean_fn, mime_type)

        src = await self.repo.create_source(
            user_id=user_id,
            workspace_id=workspace_id,
            source_type=source_type,
            filename=clean_fn,
            mime_type=mime_type,
            size_bytes=size_bytes,
            content_hash=content_hash,
            origin=origin,
            metadata={"storage_path": save_path}
        )

        return src, False

    async def delete_source_and_cleanup(self, source_id: str, user_id: str) -> bool:
        """Delete source from database and remove all physical sandbox files."""
        src = await self.repo.get_source(source_id, user_id)
        if not src:
            return False

        path = src.metadata_json.get("storage_path") if src.metadata_json else None
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.warning("File deletion cleanup notice for '%s': %s", path, e)

        return await self.repo.delete_source(source_id, user_id)

    @staticmethod
    def _determine_type(filename: str, mime_type: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in (".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md"):
            return "FILE"
        elif ext in (".xlsx", ".xls", ".csv"):
            return "FILE"
        elif ext in (".png", ".jpg", ".jpeg", ".webp"):
            return "IMAGE"
        elif ext in (".mp3", ".wav", ".m4a", ".ogg"):
            return "AUDIO"
        elif ext in (".mp4", ".webm", ".avi"):
            return "VIDEO"
        elif ext in (".py", ".js", ".ts", ".dart", ".cpp", ".c", ".html", ".css", ".sql"):
            return "CODE"
        else:
            return "FILE"
