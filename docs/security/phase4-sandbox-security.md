# Phase 4 Sandbox Security & Isolation Architecture

## Security Guarantees
1. **No Host Execution**: Code is NEVER executed directly on host processes, PowerShell, CMD, or unrestricted subprocesses.
2. **Fail Closed**: If no safe sandbox environment can be created, code execution aborts with `SANDBOX_UNAVAILABLE`.
3. **Filesystem Isolation**: Code operates strictly inside `sandbox/{execution_id}/workspace/`. Absolute paths (`/etc`, `C:\Windows`) and parent directory traversal (`../`) are blocked (`ACCESS_DENIED`).
4. **Secrets & Source Code Protection**: Access to ULTRON source code (`backend/`, `app/`, `ultron/`), `.env` files, MySQL credentials, JWT keys, and API keys is strictly prohibited.
5. **Network Isolation**: Default `DENY_ALL`. Localhost (`127.0.0.1`), private IP ranges (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`), link-local IPs (`169.254.0.0/16`), and metadata endpoints (`169.254.169.254`) are blocked (`NETWORK_DENIED`).
6. **Server-Side Limits**:
   - `CODE_EXECUTION_TIMEOUT = 10.0s`
   - `CODE_MAX_CPU_SECONDS = 10s`
   - `CODE_MAX_MEMORY_MB = 512MB`
   - `CODE_MAX_OUTPUT_BYTES = 1MB`
   - `CODE_MAX_FILE_SIZE_MB = 10MB`
   - `CODE_MAX_FILES = 100`
   - `CODE_MAX_WORKSPACE_SIZE_MB = 100MB`
   - `CODE_MAX_RETRIES = 3`
7. **Process Tree Termination**: On timeout or cancellation, process tree signal kill (`taskkill /F /T` / `SIGKILL`) terminates all spawned processes.
8. **Ownership Verification**: All workspace, file, and execution operations validate user tenancy (`user_id`, `execution_id`, `task_id`, `workspace_id`).
