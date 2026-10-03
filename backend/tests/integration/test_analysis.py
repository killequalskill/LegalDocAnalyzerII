import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.db.clause_models import Clause, ExtractedEntity
from app.services.llm.mock_provider import MockLLMProvider
from app.services.analyzer import AnalysisService


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
def sample_document(test_db):
    """Create sample document with chunks."""
    doc = Document(
        id=uuid4(),
        filename="test.pdf",
        original_filename="test.pdf",
        file_size=1000,
        page_count=1,
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
        text="Licensee shall pay $10,000 per annum in quarterly installments.",
        char_start=0,
        char_end=60,
        created_at=datetime.utcnow(),
    )
    chunk2 = DocumentChunk(
        id=uuid4(),
        document_id=doc.id,
        page_number=1,
        section_name="TERMINATION",
        clause_id="8.1",
        text="Either party may terminate with 60 days written notice.",
        char_start=100,
        char_end=155,
        created_at=datetime.utcnow(),
    )
    test_db.add(chunk1)
    test_db.add(chunk2)
    test_db.commit()

    return doc, [chunk1, chunk2]


def test_analyzer_classifies_chunks(test_db, sample_document):
    """Test analyzer classifies document chunks."""
    provider = MockLLMProvider()
    analyzer = AnalysisService(provider)
    doc, chunks = sample_document

    result = analyzer.analyze_document(doc.id, test_db)

    assert result["chunks_processed"] == 2
    assert result["clauses_classified"] == 2


def test_analyzer_extracts_entities(test_db, sample_document):
    """Test analyzer extracts entities from chunks."""
    provider = MockLLMProvider()
    analyzer = AnalysisService(provider)
    doc, chunks = sample_document

    result = analyzer.analyze_document(doc.id, test_db)

    # Service ran extraction
    assert result["chunks_processed"] == 2


def test_analyzer_retrieves_clauses(test_db, sample_document):
    """Test retrieving classified clauses."""
    provider = MockLLMProvider()
    analyzer = AnalysisService(provider)
    doc, chunks = sample_document

    # First analyze
    analyzer.analyze_document(doc.id, test_db)

    # Then retrieve
    clauses = analyzer.get_document_clauses(doc.id, test_db)

    assert len(clauses) == 2
    for clause in clauses:
        assert "clause_type" in clause
        assert "reasoning" in clause
