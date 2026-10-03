from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.models.flags import ReviewFlagsResponse
from app.services.flagging_service import FlaggingService
from app.services.llm.openai_provider import OpenAIProvider

router = APIRouter()


def get_flagging_service():
    """Dependency to provide flagging service."""
    try:
        llm_provider = OpenAIProvider()
    except Exception:
        from app.services.llm.mock_provider import MockLLMProvider
        llm_provider = MockLLMProvider()

    return FlaggingService(llm_provider)


@router.post(
    "/documents/{document_id}/analyze-risks",
    response_model=ReviewFlagsResponse,
    tags=["analysis"],
)
def analyze_risks(
    document_id: str,
    use_semantic_analysis: bool = True,
    db: Session = Depends(get_db),
    flagging_service: FlaggingService = Depends(get_flagging_service),
) -> ReviewFlagsResponse:
    """
    Analyze a document for risks and noteworthy clauses.

    This generates flags for human review—NOT legal advice.

    Flags include:
    - Missing critical clauses
    - Unusual amounts or terms
    - Asymmetric obligations
    - Short notice periods
    - Auto-renewal provisions
    - Broad liability waivers
    - Vague obligations (semantic analysis)

    Each flag has:
    - Category (what type of issue)
    - Severity (low/medium/high)
    - Reason (explanation for review)
    - Source (page, clause, exact text)
    - Is-rule-based (deterministic vs LLM-generated)
    """
    try:
        result = flagging_service.flag_document(
            document_id=UUID(document_id),
            db=db,
            use_semantic_analysis=use_semantic_analysis,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")


@router.get(
    "/documents/{document_id}/flags",
    response_model=ReviewFlagsResponse,
    tags=["analysis"],
)
def get_flags(
    document_id: str,
    db: Session = Depends(get_db),
    flagging_service: FlaggingService = Depends(get_flagging_service),
) -> ReviewFlagsResponse:
    """Retrieve previously generated risk flags for a document."""
    try:
        result = flagging_service.get_document_flags(
            document_id=UUID(document_id),
            db=db,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
