from typing import List, Literal
from sqlalchemy.orm import Session
from uuid import UUID
from app.services.vector_retriever import VectorRetriever
from app.services.bm25_retriever import BM25Retriever
from app.services.embeddings import EmbeddingService


class HybridRetriever:
    """
    Hybrid retrieval combining BM25 (lexical) and vector (semantic) search.

    Strategy:
    1. Get top-k results from both BM25 and vector search
    2. Normalize scores to 0-1 range
    3. Combine with weighted average (configurable)
    4. Re-rank and return top-k
    """

    def __init__(
        self,
        embedding_service: EmbeddingService = None,
        alpha: float = 0.5,
    ):
        """
        Initialize hybrid retriever.

        Args:
            embedding_service: EmbeddingService instance
            alpha: Weight for BM25 (0.0-1.0)
                  - 0.5 means 50% BM25, 50% vector
                  - 0.7 means 70% BM25, 30% vector
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_retriever = VectorRetriever(self.embedding_service)
        self.bm25_retriever = BM25Retriever()
        self.alpha = alpha

    def retrieve(
        self,
        query: str,
        document_id: UUID,
        db: Session,
        top_k: int = 5,
        method: Literal["bm25", "vector", "hybrid"] = "hybrid",
    ) -> List[dict]:
        """
        Retrieve chunks using specified method.

        Args:
            query: Query text
            document_id: Document UUID
            db: Database session
            top_k: Number of results to return
            method: "bm25", "vector", or "hybrid"
        """
        if method == "bm25":
            return self.bm25_retriever.retrieve(query, document_id, db, top_k)
        elif method == "vector":
            return self.vector_retriever.retrieve(query, document_id, db, top_k)
        elif method == "hybrid":
            return self._hybrid_retrieve(query, document_id, db, top_k)
        else:
            raise ValueError(f"Unknown retrieval method: {method}")

    def _hybrid_retrieve(
        self,
        query: str,
        document_id: UUID,
        db: Session,
        top_k: int,
    ) -> List[dict]:
        """
        Combine BM25 and vector retrieval with weighted scoring.
        """
        # Get results from both methods
        bm25_results = self.bm25_retriever.retrieve(query, document_id, db, top_k=top_k)
        vector_results = self.vector_retriever.retrieve(query, document_id, db, top_k=top_k)

        # Merge by chunk_id, combining scores
        merged = {}

        for result in bm25_results:
            chunk_id = result["chunk_id"]
            merged[chunk_id] = result.copy()
            merged[chunk_id]["bm25_score"] = result["score"]
            merged[chunk_id]["vector_score"] = 0.0

        for result in vector_results:
            chunk_id = result["chunk_id"]
            if chunk_id not in merged:
                merged[chunk_id] = result.copy()
                merged[chunk_id]["bm25_score"] = 0.0
                merged[chunk_id]["vector_score"] = result["score"]
            else:
                merged[chunk_id]["vector_score"] = result["score"]

        # Compute hybrid score: weighted combination
        for chunk_id in merged:
            bm25_score = merged[chunk_id]["bm25_score"]
            vector_score = merged[chunk_id]["vector_score"]
            hybrid_score = self.alpha * bm25_score + (1 - self.alpha) * vector_score
            merged[chunk_id]["score"] = hybrid_score

        # Sort by hybrid score and return top-k
        results = sorted(
            merged.values(),
            key=lambda x: x["score"],
            reverse=True,
        )[:top_k]

        return results
