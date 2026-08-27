import pytest
from app.tools.filesystem import filesystem_read, filesystem_write, _resolve_sandboxed_path
from app.ai.model_manager import ModelManager


def test_sandbox_path_traversal_protection():
    # Valid write inside sandbox
    res = filesystem_write("test_note.txt", "Sandboxed content")
    assert "Sandboxed content" in filesystem_read("test_note.txt")

    # Path traversal attempts must raise PermissionError
    with pytest.raises(PermissionError):
        _resolve_sandboxed_path("../outside.txt")

    with pytest.raises(PermissionError):
        _resolve_sandboxed_path("../../secret.env")

    with pytest.raises(PermissionError):
        _resolve_sandboxed_path("C:\\Windows\\System32\\cmd.exe")


@pytest.mark.asyncio
async def test_model_manager_unsupported_provider():
    mm = ModelManager(provider="unsupported_provider_xyz")
    with pytest.raises(ValueError):
        await mm.generate("Hello")
