from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    raw_response: Optional[Dict[str, Any]] = None
    structured_data: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Generates text completion for a given prompt.
        """
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema_class: type, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a structured JSON output validated against a Pydantic schema class.
        """
        pass
