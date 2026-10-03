from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Base response from LLM calls."""
    content: str
    model: str
    tokens_used: Optional[int] = None


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def call(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Call LLM with prompt and optional system message.
        Must return structured LLMResponse.
        """
        pass

    @abstractmethod
    def call_with_schema(
        self,
        prompt: str,
        schema: type,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """
        Call LLM requesting JSON output conforming to schema.
        Returns parsed JSON dict.
        """
        pass
