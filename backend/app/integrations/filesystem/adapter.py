import os
import logging
from typing import Dict, Any, List
from app.integrations.contracts import IntegrationDescriptor, OperationDescriptor
from app.integrations.integration_registry import integration_registry
from app.integrations.filesystem.models import FileEntryModel

logger = logging.getLogger("ULTRON.Integrations.FilesystemAdapter")


class FilesystemAdapter:
    """Secure Filesystem Adapter wrapping process sandbox workspace directory operations."""

    INTEGRATION_ID = "filesystem"

    def __init__(self, base_workspace_path: str = "sandbox/workspace_default"):
        self.base_dir = os.path.abspath(base_workspace_path)
        os.makedirs(self.base_dir, exist_ok=True)
        self._register_descriptor()

    def _register_descriptor(self):
        desc = IntegrationDescriptor(
            id=self.INTEGRATION_ID,
            name="Filesystem",
            version="1.0.0",
            provider="SandboxFS",
            description="Secure Isolated Process Sandbox Filesystem Integration",
            capabilities=["sandbox", "code"],
            risk_level="MEDIUM",
            authentication_type="NONE",
            required_scopes=["READ_WORKSPACE", "READ_FILE", "WRITE_FILE", "CREATE_FILE", "DELETE_FILE"],
            supported_operations={
                "list_workspace": OperationDescriptor(
                    operation_id="list_workspace",
                    description="List files in secure workspace",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["READ_WORKSPACE"]
                ),
                "read_file": OperationDescriptor(
                    operation_id="read_file",
                    description="Read file contents from workspace",
                    risk_level="LOW",
                    requires_approval=False,
                    required_scopes=["READ_FILE"]
                ),
                "write_file": OperationDescriptor(
                    operation_id="write_file",
                    description="Write content to a file in workspace",
                    risk_level="MEDIUM",
                    requires_approval=False,
                    required_scopes=["WRITE_FILE"]
                )
            }
        )
        integration_registry.register(desc)

    def _validate_safe_path(self, relative_path: str) -> str:
        target = os.path.abspath(os.path.join(self.base_dir, relative_path))
        if not target.startswith(self.base_dir):
            raise PermissionError("PATH_TRAVERSAL_DENIED: Path escapes sandbox workspace jail.")
        return target

    async def execute(self, operation_id: str, parameters: Dict[str, Any]) -> Any:
        op = operation_id.lower()
        if op == "list_workspace":
            entries = []
            if os.path.exists(self.base_dir):
                for f in os.listdir(self.base_dir):
                    fp = os.path.join(self.base_dir, f)
                    entry = FileEntryModel(
                        filename=f,
                        filepath=fp,
                        size_bytes=os.path.getsize(fp) if os.path.isfile(fp) else 0,
                        is_directory=os.path.isdir(fp)
                    )
                    entries.append(entry.model_dump() if hasattr(entry, "model_dump") else entry.dict())
            return entries

        elif op == "read_file":
            filename = parameters.get("filename", "output.txt")
            safe_path = self._validate_safe_path(filename)
            if not os.path.exists(safe_path):
                return {"error": "File not found", "content": ""}
            with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
                return {"filename": filename, "content": f.read()}

        elif op == "write_file":
            filename = parameters.get("filename", "output.txt")
            content = parameters.get("content", "")
            safe_path = self._validate_safe_path(filename)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"written": True, "filename": filename, "bytes": len(content)}

        else:
            raise ValueError(f"Unsupported Filesystem operation '{op}'")
