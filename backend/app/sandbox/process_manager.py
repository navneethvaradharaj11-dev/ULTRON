import os
import sys
import time
import signal
import subprocess
import logging
from typing import Dict, Any, Optional
from app.sandbox.resource_limits import ResourceLimits

logger = logging.getLogger("ULTRON.ProcessManager")


class ProcessResult:

    def __init__(
        self,
        exit_code: Optional[int] = None,
        stdout: str = "",
        stderr: str = "",
        status: str = "COMPLETED",
        duration_ms: int = 0
    ):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.status = status
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "status": self.status,
            "duration_ms": self.duration_ms
        }


class ProcessManager:
    """Subprocess manager enforcing execution timeout, output limits, and process tree termination."""

    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()

    def run_command(
        self,
        command: List_str if False else list,
        cwd: str,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> ProcessResult:
        timeout_val = timeout or self.limits.timeout_seconds
        start_t = time.time()

        if not cwd or not os.path.exists(cwd):
            try:
                os.makedirs(cwd, exist_ok=True)
            except Exception as exc:
                logger.error("Sandbox workspace initialization failed: %s", exc)
                return ProcessResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"SANDBOX_UNAVAILABLE: Sandbox workspace path '{cwd}' could not be initialized.",
                    status="SANDBOX_UNAVAILABLE",
                    duration_ms=0
                )

        # Sanitize environment: stripped host secrets

        safe_env = {
            "PATH": os.environ.get("PATH", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
            "TEMP": os.environ.get("TEMP", cwd),
            "TMP": os.environ.get("TMP", cwd),
            "PYTHONUNBUFFERED": "1",
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8"
        }
        if env:
            safe_env.update(env)

        popen_kwargs: Dict[str, Any] = {
            "cwd": cwd,
            "env": safe_env,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE
        }
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["start_new_session"] = True

        try:
            process = subprocess.Popen(command, **popen_kwargs)

            try:
                stdout_bytes, stderr_bytes = process.communicate(timeout=timeout_val)
                duration_ms = int((time.time() - start_t) * 1000)

                stdout_str = stdout_bytes.decode("utf-8", errors="replace") if stdout_bytes else ""
                stderr_str = stderr_bytes.decode("utf-8", errors="replace") if stderr_bytes else ""

                # Enforce stdout/stderr output size limit
                if len(stdout_bytes or b"") + len(stderr_bytes or b"") > self.limits.max_output_bytes:
                    stdout_str = stdout_str[:self.limits.max_output_bytes // 2] + "\n...[OUTPUT TRUNCATED: EXCEEDED SIZE LIMIT]"
                    stderr_str = stderr_str[:self.limits.max_output_bytes // 2] + "\n...[OUTPUT TRUNCATED: EXCEEDED SIZE LIMIT]"
                    return ProcessResult(
                        exit_code=process.returncode,
                        stdout=stdout_str,
                        stderr=stderr_str,
                        status="OUTPUT_LIMIT_EXCEEDED",
                        duration_ms=duration_ms
                    )

                status = "COMPLETED" if process.returncode == 0 else "FAILED"
                return ProcessResult(
                    exit_code=process.returncode,
                    stdout=stdout_str,
                    stderr=stderr_str,
                    status=status,
                    duration_ms=duration_ms
                )

            except subprocess.TimeoutExpired:
                # Force kill process tree
                self._terminate_process_tree(process)
                duration_ms = int((time.time() - start_t) * 1000)
                logger.warning("Process execution timed out after %.2f seconds", timeout_val)
                return ProcessResult(
                    exit_code=-1,
                    stdout="",
                    stderr=f"TIMEOUT: Execution exceeded time limit of {timeout_val} seconds.",
                    status="TIMEOUT",
                    duration_ms=duration_ms
                )

        except Exception as e:
            duration_ms = int((time.time() - start_t) * 1000)
            logger.error("Process execution error: %s", e)
            return ProcessResult(
                exit_code=-1,
                stdout="",
                stderr=f"PROCESS_ERROR: {str(e)}",
                status="FAILED",
                duration_ms=duration_ms
            )

    def _terminate_process_tree(self, process: subprocess.Popen):
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
                )
            else:
                try:
                    pgid = os.getpgid(process.pid)
                    if pgid != os.getpgrp():
                        os.killpg(pgid, signal.SIGKILL)
                    else:
                        process.kill()
                except Exception:
                    process.kill()
        except Exception as ex:
            logger.warning("Error terminating process tree: %s", ex)
            try:
                process.kill()
            except Exception:
                pass

        try:
            process.communicate(timeout=0.5)
        except Exception:
            pass
