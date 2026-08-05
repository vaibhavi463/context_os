from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
from dataclasses import dataclass, field
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = structlog.get_logger()


# Custom Exception Hierarchy
class LLMException(Exception):
    """Base exception for LLM provider errors."""
    pass


class LLMTimeoutException(LLMException):
    """Exception raised when LLM provider times out."""
    pass


class LLMRateLimitException(LLMException):
    """Exception raised when LLM provider rate limit is exceeded."""
    pass


class LLMProviderException(LLMException):
    """Exception raised for general LLM API failure."""
    pass


@dataclass
class LLMMessage:
    role: str  # "user", "model", "system", "tool"
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 2048,
        response_schema: Any | None = None
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def stream_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        pass


class MockLLMProvider(BaseLLMProvider):
    async def generate_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 2048,
        response_schema: Any | None = None
    ) -> LLMResponse:
        last_msg = messages[-1].content if messages else ""
        content = f"Mock AI Response to: '{last_msg}'. System status is nominal based on retrieved context."
        
        # Calculate dynamic mock tokens
        prompt_tokens = sum(len(m.content.split()) for m in messages) * 2
        completion_tokens = len(content.split()) * 2
        cost = (prompt_tokens * 0.000000075) + (completion_tokens * 0.00000030)

        return LLMResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_usd=round(cost, 6)
        )

    async def stream_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        response = await self.generate_completion(messages, tools, temperature)
        words = response.content.split()
        for word in words:
            yield word + " "


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash") -> None:
        self.api_key = api_key
        self.model_name = model_name

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Gemini 2.5 Flash Pricing ($0.075 / 1M prompt tokens, $0.30 / 1M output tokens)
        prompt_cost = (prompt_tokens / 1_000_000) * 0.075
        completion_cost = (completion_tokens / 1_000_000) * 0.30
        return round(prompt_cost + completion_cost, 6)

    @retry(
        retry=retry_if_exception_type((LLMProviderException, LLMRateLimitException)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=False
    )
    async def generate_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 2048,
        response_schema: Any | None = None
    ) -> LLMResponse:
        if not self.api_key or self.api_key.startswith("your_"):
            mock = MockLLMProvider()
            return await mock.generate_completion(messages, tools, temperature)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=max_output_tokens,
            )

            if response_schema:
                config.response_mime_type = "application/json"
                config.response_schema = response_schema

            if tools:
                tool_declarations = []
                for t in tools:
                    tool_declarations.append(
                        types.FunctionDeclaration(
                            name=t["name"],
                            description=t.get("description", ""),
                            parameters=t.get("parameters")
                        )
                    )
                config.tools = [types.Tool(function_declarations=tool_declarations)]

            contents = [msg.content for msg in messages]
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            text_out = response.text if response.text else ""
            
            # Extract Token Usage Metadata
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                prompt_tokens = response.usage_metadata.prompt_token_count or 0
                completion_tokens = response.usage_metadata.candidates_token_count or 0

            cost = self._calculate_cost(prompt_tokens, completion_tokens)

            # Parse tool calls
            parsed_tool_calls = []
            if hasattr(response, "function_calls") and response.function_calls:
                for fc in response.function_calls:
                    parsed_tool_calls.append({
                        "tool_name": fc.name,
                        "arguments": fc.args
                    })

            return LLMResponse(
                content=text_out,
                tool_calls=parsed_tool_calls if parsed_tool_calls else None,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                estimated_cost_usd=cost
            )
        except Exception as e:
            logger.warning("Gemini completion API call failed, falling back to mock provider", error=str(e))
            mock = MockLLMProvider()
            return await mock.generate_completion(messages, tools, temperature)

    async def stream_completion(
        self,
        messages: list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2
    ) -> AsyncGenerator[str, None]:
        if not self.api_key or self.api_key.startswith("your_"):
            mock = MockLLMProvider()
            async for token in mock.stream_completion(messages, tools, temperature):
                yield token
            return

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(temperature=temperature)

            contents = [msg.content for msg in messages]
            response = client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.warning("Gemini stream completion failed, falling back to mock provider", error=str(e))
            mock = MockLLMProvider()
            async for token in mock.stream_completion(messages, tools, temperature):
                yield token


def get_llm_provider() -> BaseLLMProvider:
    if settings.LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("your_"):
        return GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
    return MockLLMProvider()
