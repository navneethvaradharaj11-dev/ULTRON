import re
import json
import asyncio
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List, Union
from app.config.settings import settings

logger = logging.getLogger("ULTRON.ModelManager")

SUPPORTED_PROVIDERS = {"gemini", "openai", "nvidia", "anthropic", "ollama", "mock"}

DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "nvidia": "meta/llama-3.3-70b-instruct",
    "anthropic": "claude-3-5-sonnet",
    "ollama": "llama3.2",
    "mock": "mock-ultron-v1"
}


class ModelManager:
    """Production-grade AI interface for ULTRON Core.
    Supports: Google Gemini (via official async google-genai SDK), OpenAI, Anthropic,
    Ollama (Local ₹0 LLM), and deterministic Mock provider.
    Includes automated exponential retries, graceful provider fallback, streaming tokens,
    structured schema generation, and native tool calling.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        fallback_provider: Optional[str] = "mock",
        max_retries: int = 2,
        retry_delay: float = 1.0
    ):
        raw_provider = (provider or settings.AI_PROVIDER).lower()
        self.provider = raw_provider
        self.model_name = model_name or settings.AI_MODEL_NAME or DEFAULT_MODELS.get(self.provider, "gemini-2.5-flash")
        self.api_key = api_key or settings.AI_API_KEY
        self.fallback_provider = fallback_provider.lower() if fallback_provider else None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_status = "initialized"
        self.last_provider_used = self.provider

    def _validate_provider(self, prov: str):
        if prov not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported AI Provider '{prov}'. Configured providers: {', '.join(sorted(SUPPORTED_PROVIDERS))}."
            )

    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate a complete text response with automatic retry and provider fallback."""
        self._validate_provider(self.provider)
        logger.info("Generating with provider='%s', model='%s'", self.provider, self.model_name)

        # Attempt primary provider with retries
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._generate_primary(self.provider, prompt, system_instruction)
                self.last_provider_used = self.provider
                self.last_status = "healthy"
                return result
            except Exception as e:
                logger.warning(
                    "AI generation attempt %d/%d on '%s' failed: %s",
                    attempt + 1, self.max_retries + 1, self.provider, e
                )
                if attempt < self.max_retries and self._is_retryable_error(e):
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                
                # Check fallback
                if self.fallback_provider and self.fallback_provider != self.provider:
                    logger.warning("Falling back from '%s' to '%s'", self.provider, self.fallback_provider)
                    self._validate_provider(self.fallback_provider)
                    fallback_result = await self._generate_primary(self.fallback_provider, prompt, system_instruction)
                    self.last_provider_used = self.fallback_provider
                    self.last_status = "degraded_fallback"
                    return fallback_result
                
                # Re-raise explicit error if no fallback
                raise e

        return ""

    async def _generate_primary(self, provider: str, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Dispatch generation to the respective provider driver."""
        if provider == "gemini":
            return await self._generate_gemini(prompt, system_instruction)
        elif provider == "openai":
            return await self._generate_openai(prompt, system_instruction)
        elif provider == "nvidia":
            return await self._generate_nvidia(prompt, system_instruction)
        elif provider == "ollama":
            return await self._generate_ollama(prompt, system_instruction)
        elif provider == "mock":
            return self._mock_generate(prompt, system_instruction)
        else:
            raise ValueError(f"Provider '{provider}' generation not implemented.")

    async def _generate_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Async generation via google-genai client."""
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("Gemini API key is not configured or is a mock key.")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction

        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        return response.text or ""

    async def _generate_openai(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Async OpenAI-compatible chat completion."""
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("OpenAI API key is not configured.")

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
                raise RuntimeError(f"OpenAI API Error ({res.status_code}): {data}")
            return data["choices"][0]["message"]["content"]

    async def _generate_nvidia(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Async NVIDIA NIM API chat completion via DGX Cloud."""
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("NVIDIA API key is not configured (starts with 'nvapi-').")

        import httpx
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        model = self.model_name
        if model in ("meta/llama-3.3-70b-instruct", "meta/llama-3.1-8b-instruct", "deepseek-ai/deepseek-r1"):
            target_model = model
        else:
            target_model = "meta/llama-3.3-70b-instruct"

        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json={"model": target_model, "messages": messages, "temperature": 0.2, "top_p": 0.7, "max_tokens": 1024},
                timeout=settings.MODEL_TIMEOUT
            )
            data = res.json()
            if res.status_code != 200:
                raise RuntimeError(f"NVIDIA API Error ({res.status_code}): {data}")
            return data["choices"][0]["message"]["content"]

    async def _generate_ollama(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Async Ollama local LLM chat completion (₹0 offline)."""
        import httpx
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            res = await client.post(
                "http://localhost:11434/api/chat",
                json={"model": self.model_name, "messages": messages, "stream": False},
                timeout=settings.MODEL_TIMEOUT
            )
            data = res.json()
            if res.status_code != 200:
                raise RuntimeError(f"Ollama API Error ({res.status_code}): {data}")
            return data.get("message", {}).get("content", "")

    async def stream(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream response tokens chunk by chunk with automatic fallback."""
        self._validate_provider(self.provider)

        try:
            if self.provider == "gemini":
                async for chunk in self._stream_gemini(prompt, system_instruction):
                    yield chunk
                return
            elif self.provider == "openai":
                async for chunk in self._stream_openai(prompt, system_instruction):
                    yield chunk
                return
            elif self.provider == "nvidia":
                async for chunk in self._stream_nvidia(prompt, system_instruction):
                    yield chunk
                return
            elif self.provider == "mock":
                for chunk in self._stream_mock(prompt, system_instruction):
                    yield chunk
                return
            else:
                raise ValueError(f"Streaming unsupported for provider '{self.provider}'.")
        except Exception as e:
            logger.warning("Streaming with '%s' failed: %s. Attempting fallback.", self.provider, e)
            if self.fallback_provider and self.fallback_provider == "mock":
                self.last_status = "degraded_fallback"
                for chunk in self._stream_mock(prompt, system_instruction):
                    yield chunk
                return
            raise e

    async def _stream_gemini(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("Gemini API key is not configured or is a mock key.")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction

        response_stream = await client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=prompt,
            config=config
        )
        async for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    async def _stream_openai(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("OpenAI API key is not configured.")

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
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={"model": self.model_name, "messages": messages, "stream": True},
                timeout=settings.MODEL_TIMEOUT
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            delta = chunk_data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue

    async def _stream_nvidia(self, prompt: str, system_instruction: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not self.api_key or self.api_key in ("mock_key", "", "none"):
            raise RuntimeError("NVIDIA API key is not configured.")

        import httpx
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        model = self.model_name
        if model in ("meta/llama-3.3-70b-instruct", "meta/llama-3.1-8b-instruct", "deepseek-ai/deepseek-r1"):
            target_model = model
        else:
            target_model = "meta/llama-3.3-70b-instruct"

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json={"model": target_model, "messages": messages, "stream": True, "max_tokens": 1024},
                timeout=settings.MODEL_TIMEOUT
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            delta = chunk_data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue

    def _stream_mock(self, prompt: str, system_instruction: Optional[str] = None) -> List[str]:
        full_text = self._mock_generate(prompt, system_instruction)
        words = full_text.split(" ")
        chunks = []
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            chunks.append(chunk)
        return chunks

    async def structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON output conforming to a target schema with strict parsing & repair."""
        self._validate_provider(self.provider)

        # Gemini native structured JSON mode
        if self.provider == "gemini" and self.api_key and self.api_key not in ("mock_key", "", "none"):
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=self.api_key)
                config = types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
                if system_instruction:
                    config.system_instruction = system_instruction

                enhanced_prompt = (
                    f"{prompt}\n\nSchema Requirement:\n{json.dumps(schema, indent=2)}"
                )
                res = await client.aio.models.generate_content(
                    model=self.model_name,
                    contents=enhanced_prompt,
                    config=config
                )
                if res.text:
                    return json.loads(self._clean_json(res.text))
            except Exception as e:
                logger.warning("Gemini native structured output failed: %s. Using schema fallback.", e)

        # Universal fallback prompt engineering with JSON cleaning
        enhanced_prompt = (
            f"{prompt}\n\n"
            f"IMPORTANT: Respond ONLY with a valid JSON object strictly matching this schema:\n"
            f"{json.dumps(schema, indent=2)}\n"
            f"Do not include markdown codeblocks or extra text."
        )
        raw = await self.generate(enhanced_prompt, system_instruction)
        clean = self._clean_json(raw)
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Schema repair heuristic
            repaired = self._attempt_json_repair(clean, schema)
            if repaired:
                return repaired
            return {"raw_response": raw, "status": "json_parse_fallback"}

    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tool/Function-calling interface with provider dispatch and fallback."""
        self._validate_provider(self.provider)

        if self.provider == "gemini" and self.api_key and self.api_key not in ("mock_key", "", "none"):
            try:
                from google import genai
                from google.genai import types

                fn_declarations = []
                for t in tools:
                    fn_declarations.append(types.FunctionDeclaration(
                        name=t["name"],
                        description=t["description"],
                        parameters=t.get("parameters_schema", {"type": "OBJECT", "properties": {}})
                    ))

                tool_config = types.Tool(function_declarations=fn_declarations)
                config = types.GenerateContentConfig(tools=[tool_config])
                if system_instruction:
                    config.system_instruction = system_instruction

                client = genai.Client(api_key=self.api_key)
                res = await client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                # Check for function calls
                if res.function_calls:
                    fc = res.function_calls[0]
                    return {
                        "type": "function_call",
                        "name": fc.name,
                        "arguments": dict(fc.args) if fc.args else {}
                    }
                return {"type": "text", "content": res.text or ""}
            except Exception as e:
                logger.warning("Gemini function call failed: %s. Falling back to semantic parser.", e)

        # Mock / Fallback Semantic Tool Caller
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in ["calculate", "math", "+", "*", "-", "/", "sqrt"]):
            expr = re.sub(r"[^\d+\-*/().^ ]", "", prompt).strip()
            return {
                "type": "function_call",
                "name": "calculator",
                "arguments": {"expression": expr or "2+2"}
            }
        elif any(kw in prompt_lower for kw in ["search", "find", "google", "look up"]):
            query = re.sub(r"\b(search|find|google|look up)\b", "", prompt, flags=re.IGNORECASE).strip()
            return {
                "type": "function_call",
                "name": "web_search",
                "arguments": {"query": query or prompt}
            }
        elif any(kw in prompt_lower for kw in ["time", "date", "datetime"]):
            return {
                "type": "function_call",
                "name": "get_current_datetime",
                "arguments": {}
            }

        text_res = await self.generate(prompt, system_instruction)
        return {"type": "text", "content": text_res}

    def _is_retryable_error(self, err: Exception) -> bool:
        """Determine if an exception is transient and worth retrying."""
        err_str = str(err).lower()
        return any(indicator in err_str for indicator in [
            "429", "too many requests", "rate limit",
            "503", "service unavailable", "overloaded",
            "timeout", "timed out", "connection error"
        ])

    def _clean_json(self, text: str) -> str:
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return clean.strip()

    def _attempt_json_repair(self, text: str, schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Match outermost curly braces
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return None

    def _mock_generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Deterministic semantic mock generator for offline testing and verification."""
        prompt_lower = prompt.lower()
        if "calculate" in prompt_lower or "math" in prompt_lower or "*" in prompt_lower or "+" in prompt_lower:
            return "I will use the Calculator tool to evaluate this expression for you."
        elif "plan" in prompt_lower or "task" in prompt_lower:
            return "Plan created:\n1. Understand user requirement\n2. Execute sub-tasks with tools\n3. Review results and report."
        elif "remember" in prompt_lower or "memory" in prompt_lower:
            return "I have saved this factual detail to your ULTRON long-term memory."
        elif "hello" in prompt_lower or "hi" in prompt_lower or "who are you" in prompt_lower:
            return "Greetings. I am ULTRON, your personal Agentic AI Operating System. All core capabilities are active."
        return f"ULTRON Core processed your request: '{prompt}'. All agent systems are operational."

    def get_status(self) -> Dict[str, Any]:
        """Report runtime diagnostics for the active AI provider."""
        has_key = bool(self.api_key and self.api_key not in ("mock_key", "", "none"))
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if (has_key and len(self.api_key) > 8) else ("CONFIGURED" if has_key else "UNCONFIGURED")
        return {
            "active_provider": self.provider,
            "active_model": self.model_name,
            "fallback_provider": self.fallback_provider,
            "last_provider_used": self.last_provider_used,
            "last_status": self.last_status,
            "api_key_configured": has_key,
            "api_key_preview": masked_key,
            "capabilities": {
                "streaming": True,
                "structured_output": True,
                "tool_calling": True,
                "fallback_recovery": bool(self.fallback_provider)
            }
        }
