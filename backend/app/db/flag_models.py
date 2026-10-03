import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ReviewFlagRecord(Base):
    """Stores review flags generated during analysis."""

    __tablename__ = "review_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id"), nullable=True)
    category = Column(String(50), nullable=False)  # e.g., "missing_clause"
    severity = Column(String(20), nullable=False)  # low, medium, high
    reason = Column(Text, nullable=False)
    source_page = Column(Integer, nullable=False)
    source_clause = Column(String(50), nullable=True)  # e.g., "7.2"
    extracted_value = Column(Text, nullable=True)
    is_rule_based = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
