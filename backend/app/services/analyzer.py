from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import DocumentChunk
from app.db.clause_models import Clause, ExtractedEntity
from app.services.llm.base import LLMProvider
from app.services.clause_classifier import ClauseClassifier
from app.services.extractor import EntityExtractor
from app.models.extraction import ClauseClassificationResult, ExtractionResult


class AnalysisService:
    """
    Orchestrates clause classification and entity extraction for documents.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.classifier = ClauseClassifier(llm_provider)
        self.extractor = EntityExtractor(llm_provider)

    def analyze_document(
        self,
        document_id: UUID,
        db: Session,
    ) -> dict:
        """
        Analyze all chunks of a document:
        1. Classify each chunk
        2. Extract entities from each chunk
        3. Persist results to database
        """
        # Fetch all chunks for document
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.page_number, DocumentChunk.char_start)
            .all()
        )

        if not chunks:
            return {
                "document_id": str(document_id),
                "chunks_processed": 0,
                "clauses_classified": 0,
                "entities_extracted": 0,
            }

        clauses_created = 0
        entities_created = 0

        for chunk in chunks:
            # Classify
            classification = self.classifier.classify(chunk.text)
            clause = Clause(
                document_id=document_id,
                chunk_id=chunk.id,
                clause_type=classification.clause_type.value,
                reasoning=classification.reasoning,
                confidence=classification.confidence,
            )
            db.add(clause)
            clauses_created += 1

            # Extract entities
            extraction = self.extractor.extract(
                text=chunk.text,
                page_number=chunk.page_number,
                chunk_id=str(chunk.id),
            )

            for entity in extraction.entities:
                db_entity = ExtractedEntity(
                    document_id=document_id,
                    chunk_id=chunk.id,
                    field_name=entity.field_name,
                    value=entity.value,
                    page_number=entity.page_number,
                )
                db.add(db_entity)
                entities_created += 1

        db.commit()

        return {
            "document_id": str(document_id),
            "chunks_processed": len(chunks),
            "clauses_classified": clauses_created,
            "entities_extracted": entities_created,
        }

    def get_document_clauses(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[dict]:
        """Retrieve classified clauses for document."""
        clauses = (
            db.query(Clause)
            .filter(Clause.document_id == document_id)
            .order_by(Clause.created_at)
            .all()
        )

        return [
            {
                "id": str(clause.id),
                "chunk_id": str(clause.chunk_id),
                "clause_type": clause.clause_type,
                "reasoning": clause.reasoning,
                "confidence": clause.confidence,
                "created_at": clause.created_at.isoformat(),
            }
            for clause in clauses
        ]

    def get_document_entities(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[dict]:
        """Retrieve extracted entities for document."""
        entities = (
            db.query(ExtractedEntity)
            .filter(ExtractedEntity.document_id == document_id)
            .order_by(ExtractedEntity.page_number, ExtractedEntity.created_at)
            .all()
        )

        return [
            {
                "id": str(entity.id),
                "field_name": entity.field_name,
                "value": entity.value,
                "page_number": entity.page_number,
                "created_at": entity.created_at.isoformat(),
            }
            for entity in entities
        ]
