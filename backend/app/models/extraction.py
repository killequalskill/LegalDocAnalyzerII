from pydantic import BaseModel, Field
from typing import Optional
from app.models.clauses import ClauseType


class ClauseClassificationResult(BaseModel):
    """Result of classifying a clause."""

    clause_type: ClauseType = Field(
        description="Classified clause category"
    )
    reasoning: str = Field(
        description="Brief explanation for the classification"
    )
    confidence: Optional[float] = Field(
        default=None,
        description="Confidence score if estimable (0-1), else None"
    )


class ExtractedEntity(BaseModel):
    """A single extracted entity with source reference."""

    field_name: str = Field(
        description="Type of entity (e.g., 'notice_period', 'payment_amount')"
    )
    value: str = Field(
        description="Extracted value"
    )
    page_number: int = Field(
        description="Source page number"
    )
    chunk_id: str = Field(
        description="Source chunk ID"
    )


class ExtractionResult(BaseModel):
    """Result of extracting entities from a clause."""

    entities: list[ExtractedEntity] = Field(
        default_factory=list,
        description="Extracted entities with source references"
    )
    raw_extraction: Optional[str] = Field(
        default=None,
        description="Raw extraction text for debugging"
    )
