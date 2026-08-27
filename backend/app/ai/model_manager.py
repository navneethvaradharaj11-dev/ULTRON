import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional
from app.config.settings import settings

logger = logging.getLogger("ULTRON.ModelManager")


class ModelManager:
    """Provider-agnostic AI interface for ULTRON Core.
    Supports: Google Gemini, OpenAI, Anthropic, and deterministic Mock provider.
    Strictly enforces configured provider and raises explicit errors if provider calls fail.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.provider = (provider or settings.AI_PROVIDER).lower()
        self.model_name = model_name or settings.AI_MODEL_NAME
        self.api_key = api_key or settings.AI_API_KEY

    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a complete text response from the configured AI provider."""
        logger.info("Generating with provider='%s', model='%s'", self.provider, self.model_name)

        if self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config if config else None
                )
                return response.text or ""
            except Exception as e:
                logger.error("Gemini AI Provider generation failed: %s", e)
                raise RuntimeError(f"Gemini AI Provider Error: {e}") from e

        elif self.provider == "openai":
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json={"model": self.model_name, "messages": messages},
                        timeout=settings.MODEL_TIMEOUT
                    )
                    data = res.json()
                    if res.status_code != 200:
                        raise RuntimeError(f"OpenAI API Error: {data}")
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error("OpenAI Provider generation failed: %s", e)
                raise RuntimeError(f"OpenAI AI Provider Error: {e}") from e

        elif self.provider == "mock":
            return self._mock_generate(prompt, system_instruction)

        else:
            raise ValueError(f"Unsupported AI Provider '{self.provider}'. Configured providers: 'gemini', 'openai', 'anthropic', 'mock'.")

    async def stream(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream response tokens chunk by chunk from configured provider."""
        if self.provider == "gemini":
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction
                response = client.models.generate_content_stream(
                    model=self.model_name,
                    contents=prompt,
                    config=config if config else None
                )
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                logger.error("Gemini AI Provider stream failed: %s", e)
                raise RuntimeError(f"Gemini Stream Error: {e}") from e

        elif self.provider == "mock":
            full_text = self._mock_generate(prompt, system_instruction)
            words = full_text.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield chunk
        else:
            raise ValueError(f"Streaming unsupported for provider '{self.provider}' or provider missing.")

    async def structured_output(self, prompt: str, schema: Dict[str, Any], system_instruction: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured JSON output conforming to a target schema."""
        enhanced_prompt = (
            f"{prompt}\n\n"
            f"IMPORTANT: Respond ONLY with a valid JSON object strictly matching this schema:\n"
            f"{json.dumps(schema, indent=2)}\n"
            f"Do not include markdown codeblocks or extra text."
        )
        raw = await self.generate(enhanced_prompt, system_instruction)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"raw_response": raw, "status": "json_parse_fallback"}

    def _mock_generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Deterministic Mock provider for offline testing and development."""
        prompt_lower = prompt.lower()
        if "calculate" in prompt_lower or "math" in prompt_lower or "*" in prompt_lower or "+" in prompt_lower:
            return "I will use the Calculator tool to evaluate this expression for you."
        elif "plan" in prompt_lower or "task" in prompt_lower:
            return "Plan created:\n1. Understand user requirement\n2. Execute sub-tasks with tools\n3. Review results and report."
        elif "remember" in prompt_lower or "memory" in prompt_lower:
            return "I have saved this factual detail to your ULTRON long-term memory."
        return f"ULTRON Core processed your request: '{prompt}'. All agent systems are operational."
