import pytest
from app.services.llm.mock_provider import MockLLMProvider
from app.services.llm.base import LLMResponse


def test_mock_provider_returns_response():
    """Test mock provider returns valid LLMResponse."""
    provider = MockLLMProvider()

    response = provider.call("test prompt")

    assert isinstance(response, LLMResponse)
    assert response.model == "mock-model"
    assert response.tokens_used == 10


def test_mock_provider_tracks_calls():
    """Test mock provider tracks calls."""
    provider = MockLLMProvider()

    assert provider.call_count == 0

    provider.call("prompt 1")
    assert provider.call_count == 1
    assert provider.last_prompt == "prompt 1"

    provider.call("prompt 2")
    assert provider.call_count == 2
    assert provider.last_prompt == "prompt 2"


def test_mock_provider_schema_response():
    """Test mock provider can return schema-conforming JSON."""
    from pydantic import BaseModel

    provider = MockLLMProvider()

    class TestSchema(BaseModel):
        name: str = "default"
        value: int = 0

    result = provider.call_with_schema("test", TestSchema)

    assert isinstance(result, dict)
