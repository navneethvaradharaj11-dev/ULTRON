from dataclasses import dataclass
from app.config.settings import settings


@dataclass
class ResourceLimits:
    """Server-side enforced resource limits for code execution."""

    timeout_seconds: float = settings.CODE_EXECUTION_TIMEOUT
    max_cpu_seconds: int = settings.CODE_MAX_CPU_SECONDS
    max_memory_mb: int = settings.CODE_MAX_MEMORY_MB
    max_output_bytes: int = settings.CODE_MAX_OUTPUT_BYTES
    max_file_size_mb: int = settings.CODE_MAX_FILE_SIZE_MB
    max_files: int = settings.CODE_MAX_FILES
    max_processes: int = settings.CODE_MAX_PROCESSES
    max_retries: int = settings.CODE_MAX_RETRIES
    max_executions_per_task: int = settings.CODE_MAX_EXECUTIONS_PER_TASK
    max_workspace_size_mb: int = settings.CODE_MAX_WORKSPACE_SIZE_MB

    def to_dict(self) -> dict:
        return {
            "timeout_seconds": self.timeout_seconds,
            "max_cpu_seconds": self.max_cpu_seconds,
            "max_memory_mb": self.max_memory_mb,
            "max_output_bytes": self.max_output_bytes,
            "max_file_size_mb": self.max_file_size_mb,
            "max_files": self.max_files,
            "max_processes": self.max_processes,
            "max_retries": self.max_retries,
            "max_executions_per_task": self.max_executions_per_task,
            "max_workspace_size_mb": self.max_workspace_size_mb,
        }
