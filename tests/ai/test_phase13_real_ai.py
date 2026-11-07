import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.ai.model_manager import ModelManager, SUPPORTED_PROVIDERS, DEFAULT_MODELS
from app.ai.context import ContextBuilder
from app.security.authentication import create_access_token


@pytest.fixture
async def test_jwt():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        username = "ai_tester_phase13"
        # Register user if not exists
        await client.post("/api/v1/auth/register", json={
            "username": username,
            "email": "ai_tester_phase13@ultron.internal",
            "password": "SecurePassword123!"
        })
        # Login to obtain real token
        login_res = await client.post("/api/v1/auth/login", data={
            "username": username,
            "password": "SecurePassword123!"
        })
        if login_res.status_code == 200:
            return login_res.json()["access_token"]
        return create_access_token(data={"sub": username, "role": "admin"})


@pytest.mark.asyncio
async def test_1_model_manager_gemini_init_and_status():
    mm = ModelManager(provider="gemini", model_name="gemini-2.5-flash", api_key="test_key_123456789")
    status = mm.get_status()

    assert status["active_provider"] == "gemini"
    assert status["active_model"] == "gemini-2.5-flash"
    assert status["api_key_configured"] is True
    assert "test..." in status["api_key_preview"]
    assert status["capabilities"]["streaming"] is True
    assert status["capabilities"]["structured_output"] is True
    assert status["capabilities"]["tool_calling"] is True
    assert status["capabilities"]["fallback_recovery"] is True


@pytest.mark.asyncio
async def test_2_model_manager_fallback_on_unconfigured_key():
    # If API key is mock or missing, it should fall back to mock provider gracefully without crashing
    mm = ModelManager(provider="gemini", api_key="mock_key", fallback_provider="mock")
    res = await mm.generate("Hello ULTRON, what is the plan?")
    
    assert res is not None
    assert len(res) > 0
    assert mm.last_provider_used == "mock"
    assert mm.last_status == "degraded_fallback"


@pytest.mark.asyncio
async def test_3_model_manager_retry_on_transient_error():
    mm = ModelManager(provider="gemini", api_key="real_looking_key", fallback_provider="mock", max_retries=1, retry_delay=0.01)

    with patch.object(mm, "_generate_gemini", side_effect=[
        RuntimeError("429 Too Many Requests: Rate limit exceeded"),
        "Recovered from transient error!"
    ]):
        res = await mm.generate("Test prompt")
        assert res == "Recovered from transient error!"
        assert mm.last_provider_used == "gemini"
        assert mm.last_status == "healthy"


@pytest.mark.asyncio
async def test_4_model_manager_streaming_generation():
    mm = ModelManager(provider="mock")
    chunks = []
    async for chunk in mm.stream("Please calculate the summary of this task"):
        chunks.append(chunk)

    full_text = "".join(chunks)
    assert len(chunks) > 1
    assert "Calculator" in full_text or "ULTRON" in full_text


@pytest.mark.asyncio
async def test_5_model_manager_structured_output():
    mm = ModelManager(provider="mock")
    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "confidence": {"type": "number"}
        },
        "required": ["status", "confidence"]
    }

    # Test with valid JSON response simulation
    with patch.object(mm, "generate", return_value='```json\n{"status": "SUCCESS", "confidence": 0.98}\n```'):
        data = await mm.structured_output("Analyze request", schema)
        assert data["status"] == "SUCCESS"
        assert data["confidence"] == 0.98


@pytest.mark.asyncio
async def test_6_model_manager_tool_calling_interface():
    mm = ModelManager(provider="mock")
    tools = [
        {
            "name": "calculator",
            "description": "Performs arithmetic calculations",
            "parameters_schema": {
                "type": "OBJECT",
                "properties": {"expression": {"type": "STRING"}}
            }
        },
        {
            "name": "web_search",
            "description": "Searches the web for latest queries",
            "parameters_schema": {
                "type": "OBJECT",
                "properties": {"query": {"type": "STRING"}}
            }
        }
    ]

    # Math query should trigger calculator tool call
    calc_call = await mm.generate_with_tools("Please calculate 45 * 12", tools)
    assert calc_call["type"] == "function_call"
    assert calc_call["name"] == "calculator"
    assert "45" in calc_call["arguments"]["expression"]

    # Search query should trigger web_search tool call
    search_call = await mm.generate_with_tools("Please search latest quantum computing benchmarks", tools)
    assert search_call["type"] == "function_call"
    assert search_call["name"] == "web_search"
    assert "quantum" in search_call["arguments"]["query"]


@pytest.mark.asyncio
async def test_7_ai_endpoints_status_and_models(test_jwt):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Status endpoint (public/internal)
        status_res = await client.get("/api/v1/ai/status")
        assert status_res.status_code == 200
        status_data = status_res.json()
        assert "active_provider" in status_data
        assert "capabilities" in status_data

        # Models endpoint
        models_res = await client.get("/api/v1/ai/models")
        assert models_res.status_code == 200
        models_data = models_res.json()
        assert "gemini" in models_data["supported_providers"]
        assert "gemini-2.5-flash" in models_data["default_models"]["gemini"]


@pytest.mark.asyncio
async def test_8_ai_endpoints_configure_and_generate(test_jwt):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": f"Bearer {test_jwt}"}

        # 1. Configure to Gemini with mock fallback
        config_res = await client.post(
            "/api/v1/ai/configure",
            headers=headers,
            json={
                "provider": "gemini",
                "model_name": "gemini-2.5-flash",
                "api_key": "mock_key",
                "fallback_provider": "mock"
            }
        )
        assert config_res.status_code == 200
        assert config_res.json()["status"] == "CONFIGURED"

        # 2. Generate text (triggers fallback cleanly)
        gen_res = await client.post(
            "/api/v1/ai/generate",
            headers=headers,
            json={"prompt": "Plan my morning tasks"}
        )
        assert gen_res.status_code == 200
        gen_data = gen_res.json()
        assert gen_data["status"] == "SUCCESS"
        assert len(gen_data["response"]) > 0

        # 3. Structured Output endpoint
        struct_res = await client.post(
            "/api/v1/ai/structured",
            headers=headers,
            json={
                "prompt": "Evaluate system health",
                "schema_definition": {
                    "type": "object",
                    "properties": {"score": {"type": "integer"}}
                }
            }
        )
        assert struct_res.status_code == 200

        # 4. Tool Dispatch endpoint
        tool_res = await client.post(
            "/api/v1/ai/tools/dispatch",
            headers=headers,
            json={"prompt": "What is the time right now?"}
        )
        assert tool_res.status_code == 200
        tool_data = tool_res.json()
        assert tool_data["status"] == "SUCCESS"
        assert tool_data["result"]["type"] == "function_call"


@pytest.mark.asyncio
async def test_9_ollama_local_llm_provider_fallback():
    mm = ModelManager(provider="ollama", model_name="llama3.2", fallback_provider="mock", max_retries=0)
    # Since local ollama isn't running on port 11434 during unit tests, it must gracefully fallback
    res = await mm.generate("Explain machine learning")
    assert res is not None
    assert len(res) > 0
    assert mm.last_provider_used == "mock"
    assert mm.last_status == "degraded_fallback"


@pytest.mark.asyncio
async def test_10_context_builder_multi_turn_history():
    cb = ContextBuilder(max_history_messages=3)
    history = [
        {"sender_name": "User", "content": "Hello, I am setting up ULTRON."},
        {"sender_name": "ULTRON", "content": "Welcome! How can I assist you today?"},
        {"sender_name": "User", "content": "Remember that my favourite programming language is Python."},
        {"sender_name": "ULTRON", "content": "I have saved that to your long-term memory."},
        {"sender_name": "User", "content": "What was the language I mentioned?"}
    ]
    memories = [
        {"memory_type": "preference", "content": "User prefers Python for data engineering"}
    ]

    prompt = cb.build_prompt_with_context(
        user_input="Remind me again",
        messages_history=history,
        memories=memories
    )

    assert "=== USER LONG-TERM MEMORIES & PREFERENCES ===" in prompt
    assert "User prefers Python" in prompt
    assert "=== RECENT CONVERSATION HISTORY ===" in prompt
    assert "User: Remind me again" in prompt
    # Truncation limit check: should only contain last 3 messages of history
    assert "Hello, I am setting up ULTRON" not in prompt
    assert "Remember that my favourite programming language is Python" in prompt


@pytest.mark.asyncio
async def test_11_nvidia_nim_multimodal_support():
    mm = ModelManager(
        provider="nvidia",
        model_name="deepseek-ai/deepseek-v4.1-flash",
        api_key="nvapi-test1234567890",
        fallback_provider="mock"
    )

    multimodal_payload = [
        {"type": "text", "text": "Describe this scene."},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRg=="}}
    ]

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "The image shows a scenic path surrounded by lush trees."}}]
        }
        mock_post.return_value = mock_resp

        result = await mm.generate(multimodal_payload)
        assert "scenic path" in result
        assert mm.last_provider_used == "nvidia"
        assert mm.model_name == "deepseek-ai/deepseek-v4.1-flash"

        # Verify request sent to NVIDIA DGX endpoint with exact format
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://integrate.api.nvidia.com/v1/chat/completions"
        sent_body = call_args[1]["json"]
        assert sent_body["model"] == "deepseek-ai/deepseek-v4.1-flash"
        assert sent_body["messages"][0]["role"] == "user"
        assert isinstance(sent_body["messages"][0]["content"], list)

