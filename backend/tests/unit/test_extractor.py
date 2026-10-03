import pytest
from app.services.llm.mock_provider import MockLLMProvider
from app.services.extractor import EntityExtractor


def test_extractor_uses_mock_provider():
    """Test extractor works with mock provider."""
    provider = MockLLMProvider()
    extractor = EntityExtractor(provider)

    text = "The Licensee shall pay $10,000 per annum with 30 days' notice to terminate."
    result = extractor.extract(
        text=text,
        page_number=5,
        chunk_id="chunk-123",
    )

    # Mock provider was called
    assert provider.call_count > 0

    # Result has expected structure
    assert hasattr(result, 'entities')
    assert hasattr(result, 'raw_extraction')


def test_extraction_preserves_source():
    """Test that extracted entities preserve source references."""
    provider = MockLLMProvider()
    extractor = EntityExtractor(provider)

    text = "Notice period: 60 days"
    result = extractor.extract(
        text=text,
        page_number=10,
        chunk_id="chunk-xyz",
    )

    # All entities should have source info
    for entity in result.entities:
        assert entity.page_number == 10
        assert entity.chunk_id == "chunk-xyz"
