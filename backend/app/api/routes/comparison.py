from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.models.comparison import ComparisonRequest, ComparisonResponse
from app.services.comparator import DocumentComparator

router = APIRouter()


def get_comparator():
    """Dependency to provide document comparator."""
    return DocumentComparator()


@router.post(
    "/documents/compare",
    response_model=ComparisonResponse,
    tags=["comparison"],
)
def compare_documents(
    request: ComparisonRequest,
    db: Session = Depends(get_db),
    comparator: DocumentComparator = Depends(get_comparator),
) -> ComparisonResponse:
    """
    Compare two versions of a document.

    Returns:
    - Added clauses
    - Removed clauses
    - Modified clauses with change summaries
    - Unchanged clauses (for reference)
    - Source page/clause references for each change

    Example changes detected:
    - "Notice period changed from 30 to 60 days"
    - "Payment amount changed from $10,000 to $15,000"
    - "Termination clause added"
    - "Confidentiality clause removed"
    """
    try:
        result = comparator.compare_documents(
            doc_v1_id=UUID(request.document_v1_id),
            doc_v2_id=UUID(request.document_v2_id),
            db=db,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
