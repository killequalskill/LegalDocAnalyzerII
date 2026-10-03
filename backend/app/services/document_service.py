import uuid
from datetime import datetime
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.db.models import Document, DocumentChunk
from app.services.document_parser import extract_text_from_pdf
from app.services.chunker import DocumentChunker
from app.core.config import settings
import os
import shutil


class DocumentService:
    """
    Service for uploading, parsing, and chunking documents.
    """

    UPLOAD_DIR = "uploads"
    MAX_FILE_SIZE = settings.max_upload_size_mb * 1024 * 1024

    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        self.chunker = DocumentChunker()

    async def upload_and_process(
        self,
        file: UploadFile,
        db: Session,
    ) -> dict:
        """
        Upload a PDF file, extract text, chunk it, and persist to database.

        Returns:
        {
            "document_id": UUID,
            "filename": str,
            "page_count": int,
            "chunk_count": int,
        }
        """
        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise ValueError("Only PDF files are supported")

        # Check file size
        file_content = await file.read()
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File size exceeds maximum of {settings.max_upload_size_mb}MB"
            )

        # Save temporarily
        temp_path = os.path.join(self.UPLOAD_DIR, f"{uuid.uuid4()}.pdf")
        with open(temp_path, "wb") as f:
            f.write(file_content)

        try:
            # Extract text
            pages = extract_text_from_pdf(temp_path)

            if not pages:
                raise ValueError("PDF contains no text content")

            # Chunk
            chunks = self.chunker.chunk_documents(pages)

            if not chunks:
                raise ValueError("No valid chunks extracted from document")

            # Create document record
            doc_id = uuid.uuid4()
            document = Document(
                id=doc_id,
                filename=f"{doc_id}.pdf",
                original_filename=file.filename,
                file_size=len(file_content),
                page_count=len(pages),
                upload_timestamp=datetime.utcnow(),
                text_extracted=datetime.utcnow(),
            )
            db.add(document)
            db.flush()

            # Create chunk records
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    page_number=chunk_data.page_number,
                    section_name=chunk_data.section_name,
                    clause_id=chunk_data.clause_id,
                    text=chunk_data.text,
                    char_start=chunk_data.char_start,
                    char_end=chunk_data.char_end,
                    created_at=datetime.utcnow(),
                )
                db.add(chunk)

            db.commit()

            return {
                "document_id": str(doc_id),
                "filename": file.filename,
                "page_count": len(pages),
                "chunk_count": len(chunks),
            }

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_document(self, document_id: str, db: Session) -> Optional[dict]:
        """Retrieve document metadata."""
        doc = db.query(Document).filter(Document.id == uuid.UUID(document_id)).first()
        if not doc:
            return None

        return {
            "id": str(doc.id),
            "original_filename": doc.original_filename,
            "file_size": doc.file_size,
            "page_count": doc.page_count,
            "upload_timestamp": doc.upload_timestamp.isoformat(),
            "text_extracted": doc.text_extracted.isoformat() if doc.text_extracted else None,
            "clauses_extracted": doc.clauses_extracted.isoformat() if doc.clauses_extracted else None,
        }

    def get_document_chunks(self, document_id: str, db: Session) -> list:
        """Retrieve all chunks for a document."""
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == uuid.UUID(document_id))
            .order_by(DocumentChunk.page_number, DocumentChunk.char_start)
            .all()
        )

        return [
            {
                "id": str(chunk.id),
                "page_number": chunk.page_number,
                "section_name": chunk.section_name,
                "clause_id": chunk.clause_id,
                "text": chunk.text,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
            }
            for chunk in chunks
        ]
