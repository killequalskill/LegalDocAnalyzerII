from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.services.analyzer import AnalysisService
from app.services.llm.openai_provider import OpenAIProvider
from app.core.config import settings

router = APIRouter()


def get_llm_provider():
    """Dependency to provide LLM provider."""
    try:
        return OpenAIProvider()
    except Exception:
        # Fallback if OpenAI not available (for testing)
        from app.services.llm.mock_provider import MockLLMProvider
        return MockLLMProvider()


@router.post("/documents/{document_id}/analyze")
def analyze_document(
    document_id: str,
    db: Session = Depends(get_db),
    llm_provider = Depends(get_llm_provider),
):
    """
    Analyze a document: classify clauses and extract entities.
    """
    try:
        analyzer = AnalysisService(llm_provider)
        result = analyzer.analyze_document(UUID(document_id), db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/documents/{document_id}/clauses")
def get_clauses(
    document_id: str,
    db: Session = Depends(get_db),
    llm_provider = Depends(get_llm_provider),
):
    """Retrieve classified clauses for a document."""
    try:
        analyzer = AnalysisService(llm_provider)
        clauses = analyzer.get_document_clauses(UUID(document_id), db)
        return {"clauses": clauses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}/entities")
def get_entities(
    document_id: str,
    db: Session = Depends(get_db),
    llm_provider = Depends(get_llm_provider),
):
    """Retrieve extracted entities for a document."""
    try:
        analyzer = AnalysisService(llm_provider)
        entities = analyzer.get_document_entities(UUID(document_id), db)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
