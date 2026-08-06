import hashlib
import math
from collections.abc import Sequence

import structlog
from app.core.config import settings

logger = structlog.get_logger()


class EmbeddingService:
    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension

    def _generate_mock_embedding(self, text: str) -> list[float]:
        """Generates a deterministic normalized 768-d vector from text SHA256 hash."""
        vec: list[float] = []
        for i in range(self.dimension):
            h = hashlib.sha256(f"{text}:{i}".encode()).digest()
            val = int.from_bytes(h[:4], byteorder="big", signed=True) / (2**31 - 1)
            vec.append(val)
        
        # Normalize to unit length for cosine similarity
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    async def get_embedding(self, text: str) -> list[float]:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your_"):
            return self._generate_mock_embedding(text)

        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=text,
            )
            if response.embedding and response.embedding.values:
                return list(response.embedding.values)
            return self._generate_mock_embedding(text)
        except Exception as e:  # noqa: BLE001
            logger.warning("Gemini embedding API call failed, falling back to mock generator", error=str(e))
            return self._generate_mock_embedding(text)

    async def get_embeddings_batch(self, texts: Sequence[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            emb = await self.get_embedding(text)
            results.append(emb)
        return results


embedding_service = EmbeddingService()
