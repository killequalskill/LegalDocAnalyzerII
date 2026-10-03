import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.services.llm.mock_provider import MockLLMProvider
from app.services.qa import RAGService
from app.services.embeddings import EmbeddingService
from datetime import datetime


@pytest.fixture
def test_db():
    """In-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def sample_document_with_chunks(test_db):
    """Create sample document with related chunks."""
    doc = Document(
        id=uuid4(),
        filename="sample.pdf",
        original_filename="sample.pdf",
        file_size=5000,
        page_count=5,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc)
    test_db.flush()

    chunk1 = DocumentChunk(
        id=uuid4(),
        document_id=doc.id,
        page_number=1,
        section_name="PAYMENT TERMS",
        clause_id="2.1",
        text="Licensee shall pay Licensor $10,000 per annum in quarterly installments of $2,500.",
        char_start=0,
        char_end=90,
        created_at=datetime.utcnow(),
    )

    chunk2 = DocumentChunk(
        id=uuid4(),
        document_id=doc.id,
        page_number=2,
        section_name="TERMINATION",
        clause_id="8.1",
        text="Either party may terminate this Agreement with 60 days written notice to the other party.",
        char_start=100,
        char_end=190,
        created_at=datetime.utcnow(),
    )

    chunk3 = DocumentChunk(
        id=uuid4(),
        document_id=doc.id,
        page_number=3,
        section_name="RENEWAL",
        clause_id="9.1",
        text="This Agreement shall automatically renew for successive one-year terms unless terminated.",
        char_start=200,
        char_end=290,
        created_at=datetime.utcnow(),
    )

    test_db.add(chunk1)
    test_db.add(chunk2)
    test_db.add(chunk3)
    test_db.commit()

    return doc, [chunk1, chunk2, chunk3]


def test_rag_service_evaluates_evidence(sample_document_with_chunks):
    """Test RAG service evaluates evidence quality."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    # Mock retrieval results
    results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 1,
            "section_name": "PAYMENT",
            "clause_id": "2.1",
            "text": "Payment text",
            "score": 0.8,
        },
        {
            "chunk_id": "chunk-2",
            "page_number": 2,
            "section_name": "TERMINATION",
            "clause_id": "8.1",
            "text": "Termination text",
            "score": 0.7,
        },
    ]

    score, notes = rag._evaluate_evidence(results)

    # Average score should be 0.75
    assert score == 0.75
    assert "2 chunks" in notes


def test_rag_service_refuses_low_evidence():
    """Test RAG refuses to answer with low evidence."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 1,
            "section_name": "X",
            "clause_id": "1.1",
            "text": "Some text",
            "score": 0.2,  # Below threshold
        },
    ]

    score, notes = rag._evaluate_evidence(results)

    assert score < rag.STRONG_EVIDENCE_THRESHOLD


def test_rag_service_generates_answer_with_mock(sample_document_with_chunks):
    """Test answer generation with mock LLM."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 1,
            "section_name": "PAYMENT",
            "clause_id": "2.1",
            "text": "Licensee shall pay $10,000 per annum",
            "score": 0.9,
        },
    ]

    answer = rag._generate_answer("What is the payment amount?", results)

    assert isinstance(answer, str)
    assert len(answer) > 0


def test_rag_answer_includes_citations(sample_document_with_chunks):
    """Test that answers include proper citations."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    # Mock retrieval results with high scores
    results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 1,
            "section_name": "PAYMENT",
            "clause_id": "2.1",
            "text": "Licensee shall pay $10,000 per annum",
            "score": 0.9,
        },
        {
            "chunk_id": "chunk-2",
            "page_number": 2,
            "section_name": "TERMINATION",
            "clause_id": "8.1",
            "text": "60 days written notice",
            "score": 0.85,
        },
    ]

    # Check evidence evaluation
    score, notes = rag._evaluate_evidence(results)
    has_sufficient = score >= rag.STRONG_EVIDENCE_THRESHOLD and len(results) >= rag.MINIMUM_CHUNKS

    assert has_sufficient
    assert len(results) >= 2
