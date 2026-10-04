import json
import re
from typing import Dict, Any, Optional
from backend.app.llm.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(api_key, model_name)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(content="[OpenAIProvider: Missing API Key - fallback text]")

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            res = await client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return LLMResponse(content=res.choices[0].message.content or "")
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return LLMResponse(content=f"[OpenAI Error: {str(e)}]")

    async def generate_structured(self, prompt: str, schema_class: type, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {}

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            res = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"}
            )
            text = res.choices[0].message.content or "{}"
            return json.loads(text)
        except Exception as e:
            print(f"OpenAI structured generation error: {e}")
            return {}
