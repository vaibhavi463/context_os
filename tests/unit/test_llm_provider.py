import pytest
from app.infrastructure.llm.provider import (
    MockLLMProvider,
    GeminiProvider,
    LLMMessage,
    LLMResponse,
    get_llm_provider
)


@pytest.mark.asyncio
async def test_mock_llm_provider_generate_completion() -> None:
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="What is the database incident status?")]
    response = await provider.generate_completion(messages)

    assert isinstance(response, LLMResponse)
    assert "Mock AI Response" in response.content
    assert response.prompt_tokens > 0
    assert response.completion_tokens > 0
    assert response.estimated_cost_usd > 0.0


@pytest.mark.asyncio
async def test_mock_llm_provider_stream_completion() -> None:
    provider = MockLLMProvider()
    messages = [LLMMessage(role="user", content="Test query")]
    tokens: list[str] = []
    async for token in provider.stream_completion(messages):
        tokens.append(token)

    assert len(tokens) > 0
    full_text = "".join(tokens)
    assert "Mock AI Response" in full_text


def test_get_llm_provider_factory() -> None:
    provider = get_llm_provider()
    assert isinstance(provider, (MockLLMProvider, GeminiProvider))
