from pydantic import BaseModel
from typing import Optional


class PageContent(BaseModel):
    """Extracted text and metadata from a single PDF page."""

    page_number: int
    text: str
    metadata: dict


class DocumentChunkData(BaseModel):
    """Structured chunk ready to persist."""

    page_number: int
    section_name: Optional[str] = None
    clause_id: Optional[str] = None
    text: str
    char_start: Optional[int] = None
    char_end: Optional[int] = None
