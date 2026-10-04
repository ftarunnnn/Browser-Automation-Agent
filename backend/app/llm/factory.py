from typing import Optional
from backend.config import settings
from backend.app.llm.base import BaseLLMProvider
from backend.app.llm.providers.gemini_provider import GeminiProvider
from backend.app.llm.providers.openai_provider import OpenAIProvider
from backend.app.llm.providers.local_provider import LocalProvider


class LLMProviderFactory:
    @staticmethod
    def get_provider(
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ) -> BaseLLMProvider:
        provider = (provider_name or settings.LLM_PROVIDER).lower()
        model = model_name or settings.LLM_MODEL

        if provider == "gemini":
            key = api_key or settings.GEMINI_API_KEY
            return GeminiProvider(api_key=key, model_name=model)
        elif provider == "openai":
            key = api_key or settings.OPENAI_API_KEY
            return OpenAIProvider(api_key=key, model_name=model)
        elif provider == "local" or provider == "mock":
            return LocalProvider(api_key="local", model_name="local-rules")
        else:
            print(f"Unknown provider '{provider}', defaulting to LocalProvider")
            return LocalProvider()


llm_factory = LLMProviderFactory()
