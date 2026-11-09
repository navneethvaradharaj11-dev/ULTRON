import os
import shutil
import logging
from typing import List, Dict, Any, Optional
from app.sandbox.resource_limits import ResourceLimits

logger = logging.getLogger("ULTRON.SandboxFilesystem")


class SandboxFilesystem:
    """Isolated filesystem manager for execution workspaces."""

    def __init__(self, execution_id: str, base_dir: Optional[str] = None, limits: Optional[ResourceLimits] = None):
        self.execution_id = execution_id
        self.limits = limits or ResourceLimits()

        # Root sandbox directory for this execution
        root_base = base_dir or os.path.join(os.getcwd(), "sandbox")
        self.sandbox_dir = os.path.abspath(os.path.join(root_base, execution_id))
        self.workspace_dir = os.path.join(self.sandbox_dir, "workspace")
        self.input_dir = os.path.join(self.sandbox_dir, "input")
        self.output_dir = os.path.join(self.sandbox_dir, "output")
        self.artifacts_dir = os.path.join(self.sandbox_dir, "artifacts")

        self.initialize_dirs()

    def initialize_dirs(self):
        """Create isolated sandbox directories."""
        for d in [self.sandbox_dir, self.workspace_dir, self.input_dir, self.output_dir, self.artifacts_dir]:
            os.makedirs(d, exist_ok=True)

    def resolve_path(self, relative_path: str) -> str:
        """Resolve and validate a relative path within the sandbox workspace directory.
        Raises ValueError if the resolved path escapes workspace_dir.
        """
        clean_rel = relative_path.lstrip("/\\").replace("\\", "/")
        target = os.path.abspath(os.path.join(self.workspace_dir, clean_rel))

        # Path traversal guard
        if not target.startswith(self.workspace_dir):
            raise ValueError(f"ACCESS_DENIED: Path '{relative_path}' escapes sandbox workspace directory.")
        return target

    def write_file(self, relative_path: str, content: str) -> str:
        """Write file within workspace with size and file count checks."""
        self._check_file_limits(relative_path, content)
        target_path = self.resolve_path(relative_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        return target_path

    def read_file(self, relative_path: str) -> str:
        """Read file from workspace."""
        target_path = self.resolve_path(relative_path)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"File '{relative_path}' not found in workspace.")
        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def delete_file(self, relative_path: str) -> bool:
        """Delete file from workspace."""
        target_path = self.resolve_path(relative_path)
        if os.path.exists(target_path):
            os.remove(target_path)
            return True
        return False

    def list_files(self) -> List[Dict[str, Any]]:
        """List all files in workspace directory."""
        files_info = []
        for root, _, filenames in os.walk(self.workspace_dir):
            for fname in filenames:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self.workspace_dir).replace("\\", "/")
                size = os.path.getsize(full)
                files_info.append({"path": rel, "size_bytes": size})
        return files_info

    def destroy(self):
        """Recursively delete the sandbox directory."""
        if os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)

    def _check_file_limits(self, relative_path: str, content: str):
        content_size_mb = len(content.encode("utf-8")) / (1024 * 1024)
        if content_size_mb > self.limits.max_file_size_mb:
            raise ValueError(f"FILE_LIMIT_EXCEEDED: File size ({content_size_mb:.2f}MB) exceeds limit of {self.limits.max_file_size_mb}MB.")

        existing_files = self.list_files()
        if len(existing_files) >= self.limits.max_files:
            target_path = self.resolve_path(relative_path)
            if not os.path.exists(target_path):
                raise ValueError(f"FILE_LIMIT_EXCEEDED: Workspace file count exceeds maximum limit of {self.limits.max_files} files.")

        total_bytes = sum(f["size_bytes"] for f in existing_files) + len(content.encode("utf-8"))
        total_mb = total_bytes / (1024 * 1024)
        if total_mb > self.limits.max_workspace_size_mb:
            raise ValueError(f"WORKSPACE_LIMIT_EXCEEDED: Workspace total size ({total_mb:.2f}MB) exceeds limit of {self.limits.max_workspace_size_mb}MB.")
