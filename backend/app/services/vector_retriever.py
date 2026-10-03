from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import DocumentChunk
from app.db.embedding_models import DocumentEmbedding
from app.services.embeddings import EmbeddingService


class VectorRetriever:
    """
    Retrieve chunks using semantic similarity via embeddings.
    Uses pgvector for similarity search.
    """

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()

    def embed_and_store(
        self,
        chunk_id: UUID,
        document_id: UUID,
        text: str,
        db: Session,
    ) -> None:
        """
        Embed a chunk and store in database.
        """
        embedding = self.embedding_service.embed_text(text)

        db_embedding = DocumentEmbedding(
            chunk_id=chunk_id,
            document_id=document_id,
            embedding=embedding,
        )
        db.add(db_embedding)
        db.commit()

    def retrieve(
        self,
        query: str,
        document_id: UUID,
        db: Session,
        top_k: int = 5,
    ) -> List[dict]:
        """
        Retrieve top-k chunks by semantic similarity to query.
        Uses cosine distance via pgvector.
        """
        query_embedding = self.embedding_service.embed_text(query)

        # Use raw SQL for vector similarity search
        # pgvector <-> operator is cosine distance (lower is more similar)
        results = db.execute(
            text("""
                SELECT
                    c.id,
                    c.page_number,
                    c.section_name,
                    c.clause_id,
                    c.text,
                    1 - (e.embedding <-> :query_embedding) as similarity
                FROM document_embeddings e
                JOIN document_chunks c ON e.chunk_id = c.id
                WHERE c.document_id = :document_id
                ORDER BY e.embedding <-> :query_embedding
                LIMIT :top_k
            """),
            {
                "query_embedding": query_embedding,
                "document_id": str(document_id),
                "top_k": top_k,
            }
        )

        return [
            {
                "chunk_id": str(row[0]),
                "page_number": row[1],
                "section_name": row[2],
                "clause_id": row[3],
                "text": row[4],
                "score": float(row[5]),  # Similarity (0-1, higher is better)
            }
            for row in results
        ]
