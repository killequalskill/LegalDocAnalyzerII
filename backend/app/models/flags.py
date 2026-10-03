from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class FlagCategory(str, Enum):
    """Categories of risk flags."""
    MISSING_CLAUSE = "missing_clause"
    ASYMMETRIC_TERMS = "asymmetric_terms"
    UNUSUAL_AMOUNT = "unusual_amount"
    SHORT_NOTICE_PERIOD = "short_notice_period"
    AUTO_RENEWAL = "auto_renewal"
    BROAD_LIABILITY_WAIVER = "broad_liability_waiver"
    RESTRICTIVE_CLAUSE = "restrictive_clause"
    VAGUE_OBLIGATION = "vague_obligation"
    UNUSUAL_TERMINATION = "unusual_termination"
    OTHER = "other"


class FlagSeverity(str, Enum):
    """Severity levels for flags."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReviewFlag(BaseModel):
    """A single review flag for human attention."""
    category: FlagCategory = Field(description="Type of flag")
    severity: FlagSeverity = Field(description="Severity: low, medium, high")
    reason: str = Field(description="Explanation of the flag (not legal advice)")
    source_page: int = Field(description="Page number where issue was found")
    source_clause: Optional[str] = Field(default=None, description="Clause ID if applicable")
    source_chunk_id: str = Field(description="Chunk ID for reference")
    extracted_value: Optional[str] = Field(
        default=None,
        description="The specific value/text that triggered the flag"
    )
    is_rule_based: bool = Field(
        default=True,
        description="True if rule-based, False if LLM-generated"
    )


class ReviewFlagsResponse(BaseModel):
    """Response containing all flags for a document."""
    document_id: str
    flags: List[ReviewFlag] = Field(default_factory=list)
    total_flags: int
    high_severity_count: int
    medium_severity_count: int
    low_severity_count: int
