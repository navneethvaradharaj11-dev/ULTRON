import math
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ULTRON.EmbeddingProvider")


class EmbeddingProvider(ABC):
    """Abstract base class for provider-independent vector embeddings."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector float array for given text."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return vector dimension count."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier name."""
        pass


class MockEmbeddingProvider(EmbeddingProvider):
    """Deterministic hash-based embedding generator for testing and offline execution."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    async def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension
        
        vector = []
        for i in range(self.dimension):
            h = hashlib.sha256(f"{text}_{i}".encode('utf-8')).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2.0 - 1.0
            vector.append(round(val, 6))

        # Normalize vector
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 6) for v in vector]
        return vector

    def get_dimension(self) -> int:
        return self.dimension

    def get_provider_name(self) -> str:
        return "mock"


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local character & term n-gram vectorizer producing normalized fixed-size embeddings."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    async def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimension

        words = text.lower().split()
        vector = [0.0] * self.dimension

        for word in words:
            for idx, char in enumerate(word):
                pos = (ord(char) * 31 + idx) % self.dimension
                vector[pos] += 1.0

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [round(v / norm, 6) for v in vector]
        return vector

    def get_dimension(self) -> int:
        return self.dimension

    def get_provider_name(self) -> str:
        return "local"


class ExternalProviderAdapter(EmbeddingProvider):
    """Adapter for external AI embedding APIs (e.g. Google GenAI, OpenAI)."""

    def __init__(self, provider_name: str = "external_google", dimension: int = 768, api_key: Optional[str] = None):
        self.provider_name = provider_name
        self.dimension = dimension
        self.api_key = api_key

    async def embed_text(self, text: str) -> List[float]:
        # If API key or remote service fails, raise exception cleanly (Never silently fallback to mock)
        if not self.api_key:
            raise RuntimeError(f"External embedding provider '{self.provider_name}' requires an API key but none was supplied.")
        
        try:
            # Simulated call or adapter hook for google-genai
            # If real call fails, raise RuntimeError to respect strict fallback contract
            raise NotImplementedError("External embedding API client requires active network credentials.")
        except Exception as e:
            logger.error("External embedding provider '%s' failed: %s", self.provider_name, e)
            raise RuntimeError(f"External embedding provider '{self.provider_name}' error: {e}") from e

    def get_dimension(self) -> int:
        return self.dimension

    def get_provider_name(self) -> str:
        return self.provider_name
