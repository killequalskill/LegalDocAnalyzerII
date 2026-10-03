import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, Vector
from app.db.base import Base


class DocumentEmbedding(Base):
    """Stores vector embeddings for document chunks."""

    __tablename__ = "document_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id"), nullable=False, unique=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    embedding = Column(Vector(384), nullable=False)  # sentence-transformers default is 384 dims
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # Index for vector similarity search
        # Note: pgvector uses HNSW or IVFFlat indexes
    )
