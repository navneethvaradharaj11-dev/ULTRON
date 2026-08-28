import pytest
from app.ai.model_manager import ModelManager


@pytest.mark.asyncio
async def test_model_manager_mock_provider():
    mm = ModelManager(provider="mock")
    res = await mm.generate("Test prompt")
    assert "ULTRON Core processed your request" in res


@pytest.mark.asyncio
async def test_model_manager_unsupported_provider_raises_error():
    with pytest.raises(ValueError, match="Unsupported AI Provider"):
        mm = ModelManager(provider="unsupported_provider_xyz")
        await mm.generate("Test prompt")
