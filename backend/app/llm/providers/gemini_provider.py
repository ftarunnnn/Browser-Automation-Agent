import json
import re
from typing import Dict, Any, Optional
from backend.app.llm.base import BaseLLMProvider, LLMResponse


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        super().__init__(api_key, model_name)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(content="[GeminiProvider: Missing API Key - fallback text]")

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            full_contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            res = client.models.generate_content(
                model=self.model_name,
                contents=full_contents
            )
            return LLMResponse(content=res.text or "")
        except Exception as e:
            print(f"Gemini generation error: {e}")
            return LLMResponse(content=f"[Gemini Error: {str(e)}]")

    async def generate_structured(self, prompt: str, schema_class: type, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        full_prompt = f"{system_prompt or ''}\n\n{prompt}\nRespond ONLY with a valid JSON object."
        res = await self.generate_text(full_prompt)
        text = res.content
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data
            except Exception as e:
                print(f"JSON parse error from Gemini output: {e}")
        return {}
