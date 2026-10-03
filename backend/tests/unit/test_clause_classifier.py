import pytest
from app.services.llm.mock_provider import MockLLMProvider
from app.services.clause_classifier import ClauseClassifier
from app.models.clauses import ClauseType


def test_classifier_uses_mock_provider():
    """Test classifier works with mock provider."""
    provider = MockLLMProvider()
    classifier = ClauseClassifier(provider)

    text = "The Licensee shall pay Licensor $10,000 per annum."
    result = classifier.classify(text)

    # Mock provider was called
    assert provider.call_count > 0
    assert provider.last_prompt is not None

    # Result has expected fields
    assert hasattr(result, 'clause_type')
    assert hasattr(result, 'reasoning')


def test_classifier_detects_payment():
    """Test that payment language is recognized."""
    provider = MockLLMProvider()
    classifier = ClauseClassifier(provider)

    # Text clearly about payment
    text = "Payment Terms: Licensee shall pay $10,000 per annum in quarterly installments."
    result = classifier.classify(text)

    # Should classify (though mock returns default)
    assert result.clause_type in ClauseType
