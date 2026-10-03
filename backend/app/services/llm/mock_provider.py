import json
from typing import Optional
from app.services.llm.base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing.
    Returns deterministic responses based on prompts.
    """

    def __init__(self):
        self.call_count = 0
        self.last_prompt = None

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Return mock response."""
        self.call_count += 1
        self.last_prompt = prompt

        return LLMResponse(
            content="Mock response for testing",
            model="mock-model",
            tokens_used=10,
        )

    def call_with_schema(
        self,
        prompt: str,
        schema: type,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Return mock JSON response matching schema."""
        self.call_count += 1
        self.last_prompt = prompt

        # Return minimal valid instance
        try:
            # Try to create empty instance
            return schema().model_dump()
        except Exception:
            # Fallback: return empty dict
            return {}
