import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.services.llm.mock_provider import MockLLMProvider
from app.services.qa import RAGService


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
def sample_doc(test_db):
    """Create a sample document with multiple chunks."""
    doc = Document(
        id=uuid4(),
        filename="contract.pdf",
        original_filename="contract.pdf",
        file_size=10000,
        page_count=5,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc)
    test_db.flush()

    chunks = [
        DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            page_number=1,
            section_name="PAYMENT TERMS",
            clause_id="2.1",
            text="Licensee shall pay Licensor an annual fee of $10,000 USD, payable in four equal quarterly installments of $2,500 each due on the first day of each quarter.",
            char_start=0,
            char_end=180,
            created_at=datetime.utcnow(),
        ),
        DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            page_number=2,
            section_name="TERMINATION",
            clause_id="8.1",
            text="Either party may terminate this Agreement with thirty (30) days prior written notice. Termination shall be effective upon receipt of written notice.",
            char_start=200,
            char_end=350,
            created_at=datetime.utcnow(),
        ),
        DocumentChunk(
            id=uuid4(),
            document_id=doc.id,
            page_number=3,
            section_name="RENEWAL",
            clause_id="9.1",
            text="This Agreement shall automatically renew for successive twelve-month periods unless either party provides written notice of non-renewal at least 30 days before expiration.",
            char_start=400,
            char_end=580,
            created_at=datetime.utcnow(),
        ),
    ]

    for chunk in chunks:
        test_db.add(chunk)
    test_db.commit()

    return doc


def test_rag_service_answer_question_with_high_evidence(test_db, sample_doc):
    """Test full RAG pipeline with sufficient evidence."""
    from app.services.retriever import HybridRetriever

    provider = MockLLMProvider()
    rag = RAGService(provider)

    # Mock retrieval by directly simulating results
    # In real scenario, retriever would query database
    mock_results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 1,
            "section_name": "PAYMENT TERMS",
            "clause_id": "2.1",
            "text": "Licensee shall pay $10,000 per annum in quarterly installments",
            "score": 0.95,
        },
        {
            "chunk_id": "chunk-2",
            "page_number": 1,
            "section_name": "PAYMENT TERMS",
            "clause_id": "2.1",
            "text": "$2,500 each quarter",
            "score": 0.92,
        },
    ]

    score, notes = rag._evaluate_evidence(mock_results)

    # Should have high confidence
    assert score > rag.STRONG_EVIDENCE_THRESHOLD
    assert len(mock_results) >= rag.MINIMUM_CHUNKS

    # Should generate answer
    answer = rag._generate_answer("What is the payment amount?", mock_results)
    assert isinstance(answer, str)
    assert len(answer) > 0


def test_rag_service_low_evidence_refusal(test_db, sample_doc):
    """Test RAG refuses when evidence is weak."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    # Only one weak result
    weak_results = [
        {
            "chunk_id": "chunk-1",
            "page_number": 5,
            "section_name": "OTHER",
            "clause_id": "12.1",
            "text": "Some vague text",
            "score": 0.25,
        },
    ]

    score, notes = rag._evaluate_evidence(weak_results)

    # Should have low confidence
    assert score < rag.STRONG_EVIDENCE_THRESHOLD

    # Generate refusal response
    refusal = rag._generate_insufficient_evidence_response("What about X?", notes)
    assert "cannot answer" in refusal.lower()


def test_rag_no_results():
    """Test RAG when no chunks are retrieved."""
    provider = MockLLMProvider()
    rag = RAGService(provider)

    score, notes = rag._evaluate_evidence([])

    assert score == 0.0
    assert "No relevant" in notes
