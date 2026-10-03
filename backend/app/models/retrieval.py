from pydantic import BaseModel
from typing import List


class RetrievalResult(BaseModel):
    """Single retrieved chunk with score."""
    chunk_id: str
    page_number: int
    section_name: str
    clause_id: str
    text: str
    score: float
    method: str = None  # bm25, vector, or hybrid


class RetrievalQuery(BaseModel):
    """Request to retrieve chunks."""
    query: str
    top_k: int = 5
    method: str = "hybrid"  # bm25, vector, or hybrid
