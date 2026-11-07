import logging
from typing import Dict, Any, Optional, List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.security.authentication import get_current_user
from app.database.models import User
from app.ai.model_manager import ModelManager, SUPPORTED_PROVIDERS, DEFAULT_MODELS
from app.tools.registry import default_tool_registry
from app.config.settings import settings

logger = logging.getLogger("ULTRON.AIEndpoint")

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])

# Shared singleton instance
_model_manager = ModelManager()


def get_model_manager() -> ModelManager:
    return _model_manager


class AIConfigureRequest(BaseModel):
    provider: str = Field(..., description="Provider name: 'gemini', 'openai', 'anthropic', 'ollama', or 'mock'")
    model_name: Optional[str] = Field(None, description="Model identifier (e.g. gemini-2.5-flash, gpt-4o-mini)")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    fallback_provider: Optional[str] = Field("mock", description="Fallback provider on failure")


class AIGenerateRequest(BaseModel):
    prompt: Union[str, List[Any], Dict[str, Any]] = Field(..., description="Input prompt for the AI model (text or multimodal parts)")
    system_instruction: Optional[str] = Field(None, description="Optional system-level directive")
    provider: Optional[str] = Field(None, description="Optional provider override")
    model_name: Optional[str] = Field(None, description="Optional model override")


class AIStructuredRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Input prompt")
    schema_definition: Dict[str, Any] = Field(..., description="JSON Schema for target structured response")
    system_instruction: Optional[str] = Field(None, description="Optional system directive")


class AIToolCallRequest(BaseModel):
    prompt: str = Field(..., description="Natural language prompt that may invoke tools")
    tool_names: Optional[List[str]] = Field(None, description="Subset of tool names to expose")


@router.get("/status")
async def get_ai_status(mm: ModelManager = Depends(get_model_manager)):
    """Retrieve operational diagnostics for the current AI Engine and active provider."""
    return mm.get_status()


@router.get("/models")
async def list_available_models():
    """Retrieve supported AI providers and recommended models."""
    return {
        "supported_providers": sorted(list(SUPPORTED_PROVIDERS)),
        "default_models": DEFAULT_MODELS,
        "available_catalogs": {
            "gemini": [
                {"id": "gemini-2.5-flash", "recommended": True, "description": "High-efficiency multimodal & reasoning model"},
                {"id": "gemini-2.5-pro", "recommended": False, "description": "Advanced multi-step reasoning & coding"},
                {"id": "gemini-1.5-flash", "recommended": False, "description": "Lightweight speed-optimized model"}
            ],
            "openai": [
                {"id": "gpt-4o-mini", "recommended": True, "description": "Fast and lightweight multimodal model"},
                {"id": "gpt-4o", "recommended": False, "description": "Omni flagship model"}
            ],
            "nvidia": [
                {"id": "deepseek-ai/deepseek-v4.1-flash", "recommended": True, "description": "DeepSeek v4.1 Flash multimodal vision & fast reasoning on NVIDIA DGX Cloud"},
                {"id": "meta/llama-3.3-70b-instruct", "recommended": True, "description": "NVIDIA DGX Cloud hosted Llama 3.3 70B (High reasoning & code)"},
                {"id": "meta/llama-3.1-8b-instruct", "recommended": False, "description": "NVIDIA DGX Cloud ultra-fast lightweight model"},
                {"id": "deepseek-ai/deepseek-r1", "recommended": False, "description": "DeepSeek R1 reasoning model on NVIDIA NIM"}
            ],
            "ollama": [
                {"id": "llama3.2", "recommended": True, "description": "Local offline lightweight model (₹0 budget)"},
                {"id": "mistral", "recommended": False, "description": "Local 7B instruction model"}
            ],
            "mock": [
                {"id": "mock-ultron-v1", "recommended": True, "description": "Air-gapped deterministic test provider"}
            ]
        }
    }


@router.post("/configure")
async def configure_ai_provider(
    req: AIConfigureRequest,
    current_user: User = Depends(get_current_user),
    mm: ModelManager = Depends(get_model_manager)
):
    """Dynamically configure active AI provider and model (Requires authenticated session)."""
    prov = req.provider.lower()
    if prov not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider '{prov}'. Must be one of: {list(SUPPORTED_PROVIDERS)}"
        )

    mm.provider = prov
    mm.model_name = req.model_name or DEFAULT_MODELS.get(prov, "gemini-2.5-flash")
    if req.api_key:
        mm.api_key = req.api_key
    if req.fallback_provider:
        mm.fallback_provider = req.fallback_provider.lower()

    # Also synchronize settings for system-wide awareness
    settings.AI_PROVIDER = mm.provider
    settings.AI_MODEL_NAME = mm.model_name
    if req.api_key:
        settings.AI_API_KEY = req.api_key

    logger.info("AI Provider dynamically configured to '%s' (model: '%s') by user '%s'", mm.provider, mm.model_name, current_user.username)
    return {
        "status": "CONFIGURED",
        "configuration": mm.get_status()
    }


@router.post("/generate")
async def generate_completion(
    req: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
    mm: ModelManager = Depends(get_model_manager)
):
    """Execute text generation with the active or requested AI provider."""
    # Create isolated or shared instance
    active_mm = mm
    if req.provider or req.model_name:
        active_mm = ModelManager(
            provider=req.provider or mm.provider,
            model_name=req.model_name or mm.model_name,
            api_key=mm.api_key,
            fallback_provider=mm.fallback_provider
        )

    try:
        response_text = await active_mm.generate(req.prompt, req.system_instruction)
        return {
            "status": "SUCCESS",
            "provider_used": active_mm.last_provider_used,
            "model_used": active_mm.model_name,
            "response": response_text
        }
    except Exception as e:
        logger.error("AI generation failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/structured")
async def generate_structured(
    req: AIStructuredRequest,
    current_user: User = Depends(get_current_user),
    mm: ModelManager = Depends(get_model_manager)
):
    """Generate structured JSON adhering to the provided JSON Schema."""
    try:
        data = await mm.structured_output(req.prompt, req.schema_definition, req.system_instruction)
        return {
            "status": "SUCCESS",
            "provider_used": mm.last_provider_used,
            "data": data
        }
    except Exception as e:
        logger.error("Structured generation failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/tools/dispatch")
async def dispatch_tool_call(
    req: AIToolCallRequest,
    current_user: User = Depends(get_current_user),
    mm: ModelManager = Depends(get_model_manager)
):
    """Test AI tool declaration and function call dispatch."""
    all_tools = default_tool_registry.list_tools()
    if req.tool_names:
        tools_to_expose = [t for t in all_tools if t["name"] in req.tool_names]
    else:
        tools_to_expose = all_tools[:5]  # Default to primary tools

    tool_call_res = await mm.generate_with_tools(req.prompt, tools_to_expose)
    return {
        "status": "SUCCESS",
        "provider_used": mm.last_provider_used,
        "result": tool_call_res
    }

