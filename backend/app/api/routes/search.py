from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.models.retrieval import RetrievalQuery
from app.services.retriever import HybridRetriever
from app.services.embeddings import EmbeddingService

router = APIRouter()


def get_retriever():
    """Dependency to provide hybrid retriever."""
    embedding_service = EmbeddingService()
    return HybridRetriever(embedding_service, alpha=0.5)


@router.post("/documents/{document_id}/retrieve")
def retrieve_chunks(
    document_id: str,
    query: RetrievalQuery,
    db: Session = Depends(get_db),
    retriever = Depends(get_retriever),
):
    """
    Retrieve relevant chunks for a query using hybrid retrieval.

    Methods:
    - bm25: Lexical ranking
    - vector: Semantic similarity
    - hybrid: Combined (default)
    """
    try:
        results = retriever.retrieve(
            query=query.query,
            document_id=UUID(document_id),
            db=db,
            top_k=query.top_k,
            method=query.method,
        )

        # Add method to each result
        for result in results:
            result["method"] = query.method

        return {"results": results, "count": len(results)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")
