import json
import os
from typing import Optional
from app.services.llm.base import LLMProvider, LLMResponse
from app.core.config import settings


class OpenAIProvider(LLMProvider):
    """Real OpenAI API provider."""

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed")

    def call(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Call OpenAI API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,  # Low temperature for consistent extraction
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            tokens_used=response.usage.total_tokens,
        )

    def call_with_schema(
        self,
        prompt: str,
        schema: type,
        system_prompt: Optional[str] = None,
    ) -> dict:
        """
        Call OpenAI with JSON schema constraint.
        Uses function calling to enforce schema.
        """
        import json
        import openai

        schema_json = schema.model_json_schema()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        # Use function calling to enforce schema
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema_json,
                    "strict": True,
                }
            },
        )

        result_text = response.choices[0].message.content
        return json.loads(result_text)
