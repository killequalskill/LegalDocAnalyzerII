import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.services.comparator import DocumentComparator
from app.models.comparison import ChangeType


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
def sample_docs_with_changes(test_db):
    """Create two document versions with known changes."""
    # Version 1 (original)
    doc_v1 = Document(
        id=uuid4(),
        filename="contract_v1.pdf",
        original_filename="contract_v1.pdf",
        file_size=5000,
        page_count=3,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc_v1)
    test_db.flush()

    chunk_v1_payment = DocumentChunk(
        id=uuid4(),
        document_id=doc_v1.id,
        page_number=1,
        section_name="PAYMENT TERMS",
        clause_id="2.1",
        text="Licensee shall pay Licensor an annual fee of $10,000 USD, payable in quarterly installments.",
        char_start=0,
        char_end=100,
        created_at=datetime.utcnow(),
    )

    chunk_v1_termination = DocumentChunk(
        id=uuid4(),
        document_id=doc_v1.id,
        page_number=2,
        section_name="TERMINATION",
        clause_id="8.1",
        text="Either party may terminate this Agreement with 30 days written notice.",
        char_start=200,
        char_end=270,
        created_at=datetime.utcnow(),
    )

    test_db.add(chunk_v1_payment)
    test_db.add(chunk_v1_termination)
    test_db.commit()

    # Version 2 (modified)
    doc_v2 = Document(
        id=uuid4(),
        filename="contract_v2.pdf",
        original_filename="contract_v2.pdf",
        file_size=5500,
        page_count=3,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc_v2)
    test_db.flush()

    # Payment amount changed from $10,000 to $15,000
    chunk_v2_payment = DocumentChunk(
        id=uuid4(),
        document_id=doc_v2.id,
        page_number=1,
        section_name="PAYMENT TERMS",
        clause_id="2.1",
        text="Licensee shall pay Licensor an annual fee of $15,000 USD, payable in quarterly installments.",
        char_start=0,
        char_end=100,
        created_at=datetime.utcnow(),
    )

    # Termination notice changed from 30 to 60 days
    chunk_v2_termination = DocumentChunk(
        id=uuid4(),
        document_id=doc_v2.id,
        page_number=2,
        section_name="TERMINATION",
        clause_id="8.1",
        text="Either party may terminate this Agreement with 60 days written notice.",
        char_start=200,
        char_end=270,
        created_at=datetime.utcnow(),
    )

    # New clause: Renewal (added in v2)
    chunk_v2_renewal = DocumentChunk(
        id=uuid4(),
        document_id=doc_v2.id,
        page_number=3,
        section_name="RENEWAL",
        clause_id="9.1",
        text="This Agreement shall automatically renew for one-year terms unless terminated.",
        char_start=300,
        char_end=380,
        created_at=datetime.utcnow(),
    )

    test_db.add(chunk_v2_payment)
    test_db.add(chunk_v2_termination)
    test_db.add(chunk_v2_renewal)
    test_db.commit()

    return doc_v1, doc_v2


def test_comparator_detects_modified_amounts(test_db, sample_docs_with_changes):
    """Test that comparator detects payment amount changes."""
    doc_v1, doc_v2 = sample_docs_with_changes
    comparator = DocumentComparator()

    result = comparator.compare_documents(doc_v1.id, doc_v2.id, test_db)

    # Should have modifications
    modified = [c for c in result.changes if c.change_type == ChangeType.MODIFIED]
    assert len(modified) >= 1

    # Check payment modification detected
    payment_changes = [c for c in modified if "PAYMENT" in (c.section_name or "")]
    assert len(payment_changes) > 0


def test_comparator_detects_modified_notice_period(test_db, sample_docs_with_changes):
    """Test that comparator detects notice period changes."""
    doc_v1, doc_v2 = sample_docs_with_changes
    comparator = DocumentComparator()

    result = comparator.compare_documents(doc_v1.id, doc_v2.id, test_db)

    modified = [c for c in result.changes if c.change_type == ChangeType.MODIFIED]

    # Should mention the day change (30 to 60)
    termination_changes = [c for c in modified if "TERMINATION" in (c.section_name or "")]
    assert len(termination_changes) > 0
    assert "days" in termination_changes[0].summary.lower()


def test_comparator_detects_added_clause(test_db, sample_docs_with_changes):
    """Test that comparator detects newly added clauses."""
    doc_v1, doc_v2 = sample_docs_with_changes
    comparator = DocumentComparator()

    result = comparator.compare_documents(doc_v1.id, doc_v2.id, test_db)

    added = [c for c in result.changes if c.change_type == ChangeType.ADDED]
    assert len(added) > 0

    # RENEWAL should be added
    renewal_added = [c for c in added if "RENEWAL" in (c.section_name or "")]
    assert len(renewal_added) > 0


def test_comparator_summary_counts(test_db, sample_docs_with_changes):
    """Test that comparator returns accurate counts."""
    doc_v1, doc_v2 = sample_docs_with_changes
    comparator = DocumentComparator()

    result = comparator.compare_documents(doc_v1.id, doc_v2.id, test_db)

    # Should have at least 1 added, 2 modified
    assert result.added_count >= 1
    assert result.modified_count >= 2
    assert result.total_changes == (result.added_count + result.removed_count + result.modified_count + result.unchanged_count)
