from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ChangeType(str, Enum):
    """Type of change between versions."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ClauseChange(BaseModel):
    """Change to a clause between two versions."""
    change_type: ChangeType
    section_name: Optional[str] = Field(description="Section name if detected")
    clause_id: Optional[str] = Field(description="Clause ID (e.g., 7.2)")

    # Version 1 (original)
    v1_text: Optional[str] = Field(default=None, description="Text in version 1")
    v1_page: Optional[int] = Field(default=None)
    v1_chunk_id: Optional[str] = Field(default=None)

    # Version 2 (new)
    v2_text: Optional[str] = Field(default=None, description="Text in version 2")
    v2_page: Optional[int] = Field(default=None)
    v2_chunk_id: Optional[str] = Field(default=None)

    # Summary
    summary: str = Field(description="Human-readable summary of the change")


class ComparisonRequest(BaseModel):
    """Request to compare two documents."""
    document_v1_id: str = Field(description="UUID of version 1 (original)")
    document_v2_id: str = Field(description="UUID of version 2 (new)")


class ComparisonResponse(BaseModel):
    """Result of comparing two document versions."""
    document_v1_id: str
    document_v2_id: str
    total_changes: int
    added_count: int
    removed_count: int
    modified_count: int
    unchanged_count: int
    changes: List[ClauseChange] = Field(default_factory=list)
