import pytest
from app.services.chunking_utils import (
    detect_section_heading,
    detect_clause_id,
    estimate_tokens,
)


def test_detect_section_heading_uppercase():
    """Test detection of uppercase section headings."""
    assert detect_section_heading("PAYMENT TERMS") is True
    assert detect_section_heading("TERMINATION") is True
    assert detect_section_heading("CONFIDENTIALITY") is True


def test_detect_section_heading_lowercase():
    """Test that regular lowercase text is not detected as heading."""
    assert detect_section_heading("This is regular text.") is False
    assert detect_section_heading("some content here") is False


def test_detect_section_heading_article():
    """Test detection of Article/Section markers."""
    assert detect_section_heading("Article 5") is True
    assert detect_section_heading("Section 3") is True
    assert detect_section_heading("ARTICLE 7") is True


def test_detect_clause_id():
    """Test clause ID extraction."""
    assert detect_clause_id("7.2") == "7.2"
    assert detect_clause_id("7.2.1") == "7.2.1"
    assert detect_clause_id("Article 5") == "Article 5"
    assert detect_clause_id("Section 3") == "Section 3"
    assert detect_clause_id("no clause id here") is None


def test_estimate_tokens():
    """Test rough token estimation."""
    text_short = "Hello world"
    text_long = "This is a much longer document with many words that should result in more tokens."

    tokens_short = estimate_tokens(text_short)
    tokens_long = estimate_tokens(text_long)

    assert tokens_short > 0
    assert tokens_long > tokens_short
