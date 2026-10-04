import json
from typing import Dict, Any, Optional
from backend.app.llm.base import BaseLLMProvider, LLMResponse


class LocalProvider(BaseLLMProvider):
    def __init__(self, api_key: str = "local", model_name: str = "local-rule-engine"):
        super().__init__(api_key, model_name)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        return LLMResponse(content="[LocalProvider Response]")

    async def generate_structured(self, prompt: str, schema_class: type, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        if "open_url" in prompt_lower or "google" in prompt_lower or "search" in prompt_lower:
            return {
                "action": "open_url",
                "url": "https://www.google.com",
                "reason": "Local rule engine selected open_url"
            }
        elif "type" in prompt_lower:
            return {
                "action": "type",
                "selector": "input[name='q']",
                "text": "Python courses",
                "reason": "Local rule engine selected type"
            }
        return {
            "action": "finish",
            "reason": "Local rule engine task complete"
        }
