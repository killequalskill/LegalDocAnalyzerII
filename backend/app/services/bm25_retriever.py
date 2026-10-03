from typing import List
from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import DocumentChunk


class BM25Retriever:
    """
    Retrieve chunks using BM25 lexical ranking.
    In-memory BM25 index built from document chunks.
    """

    def __init__(self):
        self.corpus = {}  # chunk_id -> text
        self.bm25 = None

    def index_document(
        self,
        document_id: UUID,
        db: Session,
    ) -> None:
        """
        Build BM25 index for all chunks of a document.
        """
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .all()
        )

        # Tokenize and store corpus
        corpus = []
        self.corpus = {}

        for chunk in chunks:
            # Simple tokenization (split on whitespace, lowercase)
            tokens = chunk.text.lower().split()
            corpus.append(tokens)
            self.corpus[str(chunk.id)] = chunk

        # Build BM25 index
        if corpus:
            self.bm25 = BM25Okapi(corpus)

    def retrieve(
        self,
        query: str,
        document_id: UUID,
        db: Session,
        top_k: int = 5,
    ) -> List[dict]:
        """
        Retrieve top-k chunks by BM25 score.
        """
        if not self.bm25:
            self.index_document(document_id, db)

        if not self.bm25:
            return []

        # Tokenize query
        query_tokens = query.lower().split()

        # Get BM25 scores
        scores = self.bm25.get_scores(query_tokens)

        # Sort by score descending
        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        results = []
        for idx, score in ranked:
            chunk_id = list(self.corpus.keys())[idx]
            chunk = self.corpus[chunk_id]

            # Normalize score to 0-1 range (rough approximation)
            normalized_score = min(1.0, score / 50.0)

            results.append({
                "chunk_id": chunk_id,
                "page_number": chunk.page_number,
                "section_name": chunk.section_name,
                "clause_id": chunk.clause_id,
                "text": chunk.text,
                "score": normalized_score,
            })

        return results
