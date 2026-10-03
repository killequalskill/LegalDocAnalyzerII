import pytest
from app.services.chunker import DocumentChunker
from app.models.documents import PageContent


def test_chunker_preserves_page_numbers():
    """Test that chunks preserve page numbers."""
    chunker = DocumentChunker()

    pages = [
        PageContent(
            page_number=1,
            text="SECTION 1\nThis is content on page 1.",
            metadata={},
        ),
        PageContent(
            page_number=2,
            text="SECTION 2\nThis is content on page 2.",
            metadata={},
        ),
    ]

    chunks = chunker.chunk_documents(pages)

    # Should have chunks from both pages
    page_numbers = {chunk.page_number for chunk in chunks}
    assert 1 in page_numbers
    assert 2 in page_numbers


def test_chunker_detects_sections():
    """Test that chunker detects section headings."""
    chunker = DocumentChunker()

    pages = [
        PageContent(
            page_number=1,
            text="PAYMENT TERMS\nLicensee shall pay $10,000 per annum.",
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(pages)

    assert len(chunks) > 0
    # First chunk should have detected section
    assert chunks[0].section_name == "PAYMENT TERMS"


def test_chunker_respects_size_limits():
    """Test that chunker respects token size limits."""
    chunker = DocumentChunker()

    # Create a page with very long text
    long_text = "Word " * 1000  # ~1300 tokens

    pages = [
        PageContent(
            page_number=1,
            text=long_text,
            metadata={},
        )
    ]

    chunks = chunker.chunk_documents(pages)

    # Should split into multiple chunks
    assert len(chunks) > 1

    # Each chunk should be within limits (with some tolerance)
    for chunk in chunks:
        from app.services.chunking_utils import estimate_tokens
        tokens = estimate_tokens(chunk.text)
        assert tokens <= chunker.MAX_CHUNK_TOKENS + 100  # Some tolerance
