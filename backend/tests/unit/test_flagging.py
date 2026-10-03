import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import Document, DocumentChunk
from app.db.clause_models import Clause, ExtractedEntity
from app.services.rule_flagger import RuleBasedFlagger
from app.models.clauses import ClauseType
from app.models.flags import FlagCategory, FlagSeverity


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
def sample_doc_missing_clause(test_db):
    """Document missing critical clauses."""
    doc = Document(
        id=uuid4(),
        filename="incomplete.pdf",
        original_filename="incomplete.pdf",
        file_size=2000,
        page_count=2,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc)
    test_db.flush()

    # Only has PAYMENT clause, missing TERMINATION and GOVERNING_LAW
    clause = Clause(
        document_id=doc.id,
        chunk_id=uuid4(),
        clause_type=ClauseType.PAYMENT.value,
        reasoning="Payment terms present",
        confidence=0.95,
    )
    test_db.add(clause)
    test_db.commit()

    return doc


def test_rule_flagger_detects_missing_clauses(test_db, sample_doc_missing_clause):
    """Test rule-based flagger detects missing critical clauses."""
    flagger = RuleBasedFlagger()
    flags = flagger.flag_document(sample_doc_missing_clause.id, test_db)

    # Should flag missing TERMINATION and GOVERNING_LAW
    missing_categories = {f.category for f in flags}
    assert FlagCategory.MISSING_CLAUSE in missing_categories

    # Should be high severity
    missing_flags = [f for f in flags if f.category == FlagCategory.MISSING_CLAUSE]
    assert all(f.severity == FlagSeverity.HIGH for f in missing_flags)


@pytest.fixture
def sample_doc_low_payment(test_db):
    """Document with unusually low payment amount."""
    doc = Document(
        id=uuid4(),
        filename="lowpay.pdf",
        original_filename="lowpay.pdf",
        file_size=1000,
        page_count=1,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc)
    test_db.flush()

    chunk = DocumentChunk(
        id=uuid4(),
        document_id=doc.id,
        page_number=1,
        section_name="PAYMENT",
        clause_id="2.1",
        text="Payment of $100 per year",
        char_start=0,
        char_end=25,
        created_at=datetime.utcnow(),
    )
    test_db.add(chunk)
    test_db.flush()

    # Extract entity with low amount
    entity = ExtractedEntity(
        document_id=doc.id,
        chunk_id=chunk.id,
        field_name="payment_amount",
        value="$100",
        page_number=1,
    )
    test_db.add(entity)
    test_db.commit()

    return doc


def test_rule_flagger_detects_unusual_amount(test_db, sample_doc_low_payment):
    """Test rule-based flagger flags unusually low payment amounts."""
    flagger = RuleBasedFlagger()
    flags = flagger.flag_document(sample_doc_low_payment.id, test_db)

    unusual_flags = [f for f in flags if f.category == FlagCategory.UNUSUAL_AMOUNT]
    assert len(unusual_flags) > 0
    assert unusual_flags[0].severity == FlagSeverity.MEDIUM


def test_rule_flagger_auto_renewal(test_db):
    """Test rule-based flagger detects auto-renewal."""
    doc = Document(
        id=uuid4(),
        filename="autorenewal.pdf",
        original_filename="autorenewal.pdf",
        file_size=1000,
        page_count=1,
        upload_timestamp=datetime.utcnow(),
        text_extracted=datetime.utcnow(),
    )
    test_db.add(doc)
    test_db.flush()

    clause = Clause(
        document_id=doc.id,
        chunk_id=uuid4(),
        clause_type=ClauseType.RENEWAL.value,
        reasoning="Automatic renewal every year",
        confidence=0.88,
    )
    test_db.add(clause)
    test_db.commit()

    flagger = RuleBasedFlagger()
    flags = flagger.flag_document(doc.id, test_db)

    auto_renewal_flags = [f for f in flags if f.category == FlagCategory.AUTO_RENEWAL]
    assert len(auto_renewal_flags) > 0
