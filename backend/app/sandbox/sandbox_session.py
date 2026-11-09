import os
import logging
from typing import Dict, Any, List, Optional
from app.sandbox.resource_limits import ResourceLimits
from app.sandbox.network_policy import NetworkPolicy, NetworkPolicyMode
from app.sandbox.sandbox_policy import SandboxPolicy, SandboxActionRisk
from app.sandbox.filesystem import SandboxFilesystem
from app.sandbox.process_manager import ProcessManager, ProcessResult
from app.sandbox.runtime import default_runtime_registry
from app.sandbox.artifact_manager import ArtifactManager

logger = logging.getLogger("ULTRON.SandboxSession")


class SandboxSession:
    """Active execution sandbox session binding workspace, policy, runtimes, and processes."""

    def __init__(
        self,
        execution_id: str,
        task_id: str,
        user_id: str,
        limits: Optional[ResourceLimits] = None,
        network_mode: NetworkPolicyMode = NetworkPolicyMode.DENY_ALL
    ):
        self.execution_id = execution_id
        self.task_id = task_id
        self.user_id = user_id
        self.limits = limits or ResourceLimits()
        self.network_policy = NetworkPolicy(mode=network_mode)

        self.filesystem = SandboxFilesystem(execution_id, limits=self.limits)
        self.process_manager = ProcessManager(limits=self.limits)
        self.artifact_manager = ArtifactManager(self.filesystem.artifacts_dir)
        self.runtime_registry = default_runtime_registry
        self.active = True

    # ------------------------------------------------------------------
    # File Operations
    # ------------------------------------------------------------------
    def create_file(self, relative_path: str, content: str) -> Dict[str, Any]:
        risk, reason = SandboxPolicy.evaluate_action("CREATE_FILE", path=relative_path)
        if risk == SandboxActionRisk.FORBIDDEN:
            raise PermissionError(reason)

        full_path = self.filesystem.write_file(relative_path, content)
        return {
            "path": relative_path,
            "full_path": full_path,
            "size_bytes": len(content.encode("utf-8")),
            "status": "CREATED"
        }

    def read_file(self, relative_path: str) -> str:
        risk, reason = SandboxPolicy.evaluate_action("READ_FILE", path=relative_path)
        if risk == SandboxActionRisk.FORBIDDEN:
            raise PermissionError(reason)
        return self.filesystem.read_file(relative_path)

    def update_file(self, relative_path: str, content: str) -> Dict[str, Any]:
        risk, reason = SandboxPolicy.evaluate_action("UPDATE_FILE", path=relative_path)
        if risk == SandboxActionRisk.FORBIDDEN:
            raise PermissionError(reason)

        full_path = self.filesystem.write_file(relative_path, content)
        return {
            "path": relative_path,
            "full_path": full_path,
            "size_bytes": len(content.encode("utf-8")),
            "status": "UPDATED"
        }

    def delete_file(self, relative_path: str) -> bool:
        risk, reason = SandboxPolicy.evaluate_action("DELETE_FILE", path=relative_path)
        if risk == SandboxActionRisk.FORBIDDEN:
            raise PermissionError(reason)
        return self.filesystem.delete_file(relative_path)

    def list_files(self) -> List[Dict[str, Any]]:
        return self.filesystem.list_files()

    # ------------------------------------------------------------------
    # Compilation & Execution
    # ------------------------------------------------------------------
    def compile_code(self, language: str, entrypoint: str) -> ProcessResult:
        risk, reason = SandboxPolicy.evaluate_action("COMPILE", path=entrypoint, language=language)
        if risk == SandboxActionRisk.FORBIDDEN:
            return ProcessResult(exit_code=-1, stderr=reason, status="COMPILE_ERROR")

        runtime = self.runtime_registry.get_runtime(language)
        if not runtime.is_available():
            return ProcessResult(
                exit_code=-1,
                stderr=f"RUNTIME_UNAVAILABLE: Language compiler/interpreter for '{language}' is not installed.",
                status="COMPILE_ERROR"
            )

        if not runtime.is_compiled():
            return ProcessResult(exit_code=0, stdout="No compilation required.", status="COMPLETED")

        cmd = runtime.get_compile_command(entrypoint)
        res = self.process_manager.run_command(cmd, cwd=self.filesystem.workspace_dir)
        if res.status != "COMPLETED":
            res.status = "COMPILE_ERROR"
        return res

    def execute_code(self, language: str, entrypoint: str, args: Optional[List[str]] = None) -> ProcessResult:
        risk, reason = SandboxPolicy.evaluate_action("EXECUTE", path=entrypoint, language=language)
        if risk == SandboxActionRisk.FORBIDDEN:
            return ProcessResult(exit_code=-1, stderr=reason, status="RUNTIME_ERROR")

        runtime = self.runtime_registry.get_runtime(language)
        if not runtime.is_available():
            return ProcessResult(
                exit_code=-1,
                stderr=f"RUNTIME_UNAVAILABLE: Language environment for '{language}' is not installed.",
                status="RUNTIME_ERROR"
            )

        cmd = runtime.get_run_command(entrypoint, args=args)
        res = self.process_manager.run_command(cmd, cwd=self.filesystem.workspace_dir)
        if res.status == "FAILED":
            res.status = "RUNTIME_ERROR"
        return res

    def run_tests(self, language: str, test_file: str) -> ProcessResult:
        risk, reason = SandboxPolicy.evaluate_action("RUN_TESTS", path=test_file, language=language)
        if risk == SandboxActionRisk.FORBIDDEN:
            return ProcessResult(exit_code=-1, stderr=reason, status="RUNTIME_ERROR")

        runtime = self.runtime_registry.get_runtime(language)
        if not runtime.is_available():
            return ProcessResult(
                exit_code=-1,
                stderr=f"RUNTIME_UNAVAILABLE: Language environment for '{language}' is not installed.",
                status="RUNTIME_ERROR"
            )

        cmd = runtime.get_test_command(test_file)
        return self.process_manager.run_command(cmd, cwd=self.filesystem.workspace_dir)

    def close(self):
        """Clean up session resources."""
        self.active = False
        self.filesystem.destroy()
