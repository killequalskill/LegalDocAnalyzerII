import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class Document(Base):
    """Stores document metadata and extraction status."""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    page_count = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    text_extracted = Column(DateTime, nullable=True)
    clauses_extracted = Column(DateTime, nullable=True)
    embeddings_generated = Column(DateTime, nullable=True)


class DocumentChunk(Base):
    """Stores text chunks extracted from documents with source metadata."""

    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)  # 1-indexed
    section_name = Column(String(255), nullable=True)  # e.g., "Termination"
    clause_id = Column(String(50), nullable=True)  # e.g., "7.2"
    text = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=True)  # Character offset in page
    char_end = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
