from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.document_service import DocumentService
from app.models.schemas import DocumentResponse, DocumentChunkResponse

router = APIRouter()
document_service = DocumentService()


@router.post("/documents", tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a PDF document for analysis.

    Extracts text, chunks it hierarchically, and stores to database.
    """
    try:
        result = await document_service.upload_and_process(file, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.get("/documents/{document_id}", tags=["documents"])
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve document metadata."""
    doc = document_service.get_document(document_id, db)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/documents/{document_id}/chunks", tags=["documents"])
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve all chunks for a document."""
    chunks = document_service.get_document_chunks(document_id, db)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found or has no chunks")
    return {"chunks": chunks}
