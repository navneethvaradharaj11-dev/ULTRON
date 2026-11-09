import os

SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../sandbox"))


def _resolve_sandboxed_path(file_path: str) -> str:
    """Resolve and validate that file_path resides strictly inside SANDBOX_DIR.
    Prevents path traversal attacks (../, ../../, absolute paths outside sandbox, symlink escapes).
    """
    if ":" in file_path or file_path.startswith(("\\", "/")):
        raise PermissionError(f"Access Denied: Path '{file_path}' is outside sandbox boundary.")

    os.makedirs(SANDBOX_DIR, exist_ok=True)
    real_sandbox = os.path.realpath(SANDBOX_DIR)

    # If file_path is relative, resolve relative to sandbox
    if not os.path.isabs(file_path):
        target_path = os.path.join(real_sandbox, file_path)
    else:
        target_path = file_path

    real_target = os.path.realpath(target_path)

    # Verify that target directory is inside real_sandbox
    try:
        common = os.path.commonpath([real_target, real_sandbox])
    except ValueError:
        # Different drives on Windows
        raise PermissionError(f"Access Denied: Path '{file_path}' is outside sandbox boundary.")

    if common != real_sandbox:
        raise PermissionError(f"Access Denied: Path traversal detected for '{file_path}'. Filesystem access sandboxed to '{SANDBOX_DIR}'.")

    return real_target


def filesystem_read(file_path: str) -> str:
    """Read contents of a text file strictly sandboxed within d:/ULTRON/sandbox/."""
    target_path = _resolve_sandboxed_path(file_path)
    if not os.path.exists(target_path):
        raise FileNotFoundError(f"File not found in sandbox: '{file_path}'")
    with open(target_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def filesystem_write(file_path: str, content: str) -> str:
    """Write text content to a file strictly sandboxed within d:/ULTRON/sandbox/."""
    target_path = _resolve_sandboxed_path(file_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote {len(content)} bytes to sandboxed file '{file_path}'"
