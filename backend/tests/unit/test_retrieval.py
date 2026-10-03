import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.services.embeddings import EmbeddingService
from app.services.vector_retriever import VectorRetriever
from app.services.bm25_retriever import BM25Retriever
from app.services.retriever import HybridRetriever


@pytest.fixture
def embedding_service():
    """Embedding service instance."""
    return EmbeddingService()


@pytest.fixture
def sample_chunks():
    """Sample document chunks for testing retrieval."""
    return [
        {
            "id": uuid4(),
            "page": 1,
            "section": "PAYMENT",
            "clause": "2.1",
            "text": "Licensee shall pay Licensor $10,000 per annum in quarterly installments.",
        },
        {
            "id": uuid4(),
            "page": 2,
            "section": "TERMINATION",
            "clause": "8.1",
            "text": "Either party may terminate this Agreement with 60 days written notice.",
        },
        {
            "id": uuid4(),
            "page": 3,
            "section": "CONFIDENTIALITY",
            "clause": "5.1",
            "text": "Confidential Information shall remain confidential for 3 years after termination.",
        },
        {
            "id": uuid4(),
            "page": 4,
            "section": "RENEWAL",
            "clause": "9.1",
            "text": "This Agreement shall automatically renew for successive one-year terms unless terminated.",
        },
    ]


def test_embedding_service(embedding_service):
    """Test embedding service produces vectors."""
    text = "The licensee shall pay $10,000 per annum."
    embedding = embedding_service.embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) == 384  # all-MiniLM-L6-v2 dimension
    assert all(isinstance(x, float) for x in embedding)


def test_embeddings_are_normalized(embedding_service):
    """Test that embeddings are normalized (roughly unit norm)."""
    text = "Payment clause"
    embedding = embedding_service.embed_text(text)

    # Compute L2 norm
    import math
    norm = math.sqrt(sum(x**2 for x in embedding))

    # Should be close to 1 for normalized embeddings
    assert 0.9 < norm < 1.1


def test_bm25_retriever_ranks_by_keywords(sample_chunks):
    """Test BM25 ranking by keyword match."""
    retriever = BM25Retriever()

    # Mock corpus
    corpus = {}
    for chunk in sample_chunks:
        corpus[str(chunk["id"])] = type('obj', (object,), {
            'id': chunk["id"],
            'page_number': chunk["page"],
            'section_name': chunk["section"],
            'clause_id': chunk["clause"],
            'text': chunk["text"],
        })

    retriever.corpus = corpus

    # Index with tokenized texts
    tokens_list = [chunk["text"].lower().split() for chunk in sample_chunks]
    from rank_bm25 import BM25Okapi
    retriever.bm25 = BM25Okapi(tokens_list)

    # Query: "payment amount"
    query_tokens = "payment amount".lower().split()
    scores = retriever.bm25.get_scores(query_tokens)

    # First chunk (PAYMENT) should rank highest
    assert scores[0] > scores[1]  # payment chunk > termination chunk


def test_hybrid_retriever_combines_methods(embedding_service):
    """Test hybrid retriever combines BM25 and vector results."""
    retriever = HybridRetriever(embedding_service, alpha=0.5)

    assert retriever.alpha == 0.5
    assert retriever.bm25_retriever is not None
    assert retriever.vector_retriever is not None


def test_hybrid_retriever_alpha_weighting():
    """Test alpha parameter controls weighting."""
    # Heavy BM25
    hybrid_bm25_heavy = HybridRetriever(alpha=0.8)
    assert hybrid_bm25_heavy.alpha == 0.8

    # Heavy vector
    hybrid_vector_heavy = HybridRetriever(alpha=0.2)
    assert hybrid_vector_heavy.alpha == 0.2

    # Equal
    hybrid_equal = HybridRetriever(alpha=0.5)
    assert hybrid_equal.alpha == 0.5
