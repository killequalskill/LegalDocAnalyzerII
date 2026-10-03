from pydantic import BaseModel, Field
from typing import Optional, List


class QuestionRequest(BaseModel):
    """User question about a document."""
    query: str = Field(description="Question to ask about the document")
    top_k: int = Field(default=5, description="Number of chunks to retrieve")
    retrieval_method: str = Field(
        default="hybrid",
        description="bm25, vector, or hybrid"
    )


class Citation(BaseModel):
    """Source citation for answer."""
    page_number: int
    section_name: Optional[str] = None
    clause_id: Optional[str] = None
    chunk_id: str
    text: str = Field(description="Relevant excerpt from source")


class AnswerResponse(BaseModel):
    """Response to a question."""
    query: str
    answer: str = Field(description="Generated answer")
    citations: List[Citation] = Field(
        description="Source citations supporting the answer"
    )
    evidence_score: float = Field(
        description="Confidence score (0-1) based on retrieval relevance"
    )
    has_sufficient_evidence: bool = Field(
        description="Whether evidence was sufficient to answer confidently"
    )
    evidence_notes: str = Field(
        description="Explanation of evidence quality"
    )
