import pytest
from backend.app.llm.factory import LLMProviderFactory
from backend.app.llm.providers.local_provider import LocalProvider
from backend.app.llm.providers.gemini_provider import GeminiProvider
from backend.app.llm.providers.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_llm_factory_instantiation():
    local_p = LLMProviderFactory.get_provider("local")
    assert isinstance(local_p, LocalProvider)

    gemini_p = LLMProviderFactory.get_provider("gemini", api_key="dummy_key")
    assert isinstance(gemini_p, GeminiProvider)

    openai_p = LLMProviderFactory.get_provider("openai", api_key="dummy_key")
    assert isinstance(openai_p, OpenAIProvider)


@pytest.mark.asyncio
async def test_local_llm_provider_generation():
    provider = LocalProvider()
    res_text = await provider.generate_text("Search for courses")
    assert res_text.content is not None

    res_struct = await provider.generate_structured("Search for courses", dict)
    assert "action" in res_struct
