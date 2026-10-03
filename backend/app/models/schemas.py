from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class DocumentCreate(BaseModel):
    """Request schema for document upload."""

    filename: str
    file_size: int
    page_count: int


class DocumentResponse(BaseModel):
    """Response schema for document metadata."""

    id: UUID
    filename: str
    original_filename: str
    file_size: int
    page_count: int
    upload_timestamp: datetime
    text_extracted: Optional[datetime] = None
    clauses_extracted: Optional[datetime] = None
    embeddings_generated: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    """Response schema for document chunks."""

    id: UUID
    document_id: UUID
    page_number: int
    section_name: Optional[str] = None
    clause_id: Optional[str] = None
    text: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    app_name: str
    environment: str
