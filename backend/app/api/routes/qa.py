from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.models.qa import QuestionRequest, AnswerResponse
from app.services.qa import RAGService
from app.services.llm.openai_provider import OpenAIProvider
from app.services.embeddings import EmbeddingService

router = APIRouter()


def get_rag_service():
    """Dependency to provide RAG service."""
    try:
        llm_provider = OpenAIProvider()
    except Exception:
        from app.services.llm.mock_provider import MockLLMProvider
        llm_provider = MockLLMProvider()

    embedding_service = EmbeddingService()
    return RAGService(llm_provider, embedding_service)


@router.post(
    "/documents/{document_id}/query",
    response_model=AnswerResponse,
    tags=["qa"],
)
def ask_question(
    document_id: str,
    request: QuestionRequest,
    db: Session = Depends(get_db),
    rag_service: RAGService = Depends(get_rag_service),
) -> AnswerResponse:
    """
    Ask a question about a document and get a grounded answer with citations.

    The system:
    1. Retrieves relevant chunks using hybrid retrieval
    2. Evaluates evidence quality
    3. Generates answer if evidence is sufficient
    4. Attaches citations with page numbers and source text
    5. Returns confidence score
    """
    try:
        result = rag_service.answer_question(
            query=request.query,
            document_id=UUID(document_id),
            db=db,
            top_k=request.top_k,
            retrieval_method=request.retrieval_method,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")
