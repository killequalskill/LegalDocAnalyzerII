from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import Document
from app.db.flag_models import ReviewFlagRecord
from app.services.rule_flagger import RuleBasedFlagger
from app.services.semantic_flagger import SemanticFlagger
from app.services.llm.base import LLMProvider
from app.models.flags import ReviewFlag, ReviewFlagsResponse, FlagSeverity


class FlaggingService:
    """
    Orchestrates risk flagging: rule-based + semantic analysis.
    """

    def __init__(self, llm_provider: LLMProvider = None):
        self.rule_flagger = RuleBasedFlagger()
        self.semantic_flagger = SemanticFlagger(llm_provider) if llm_provider else None

    def flag_document(
        self,
        document_id: UUID,
        db: Session,
        use_semantic_analysis: bool = True,
    ) -> ReviewFlagsResponse:
        """
        Analyze document for risk flags.

        Process:
        1. Apply deterministic rules
        2. Optionally apply semantic analysis via LLM
        3. Persist flags to database
        4. Return summary
        """
        all_flags = []

        # Rule-based flagging (always run)
        rule_flags = self.rule_flagger.flag_document(document_id, db)
        all_flags.extend(rule_flags)

        # Semantic flagging (optional, requires LLM)
        if use_semantic_analysis and self.semantic_flagger:
            from app.db.models import DocumentChunk
            chunks = (
                db.query(DocumentChunk)
                .filter(DocumentChunk.document_id == document_id)
                .all()
            )

            for chunk in chunks[:10]:  # Limit to first 10 to avoid excessive LLM calls
                semantic_flags = self.semantic_flagger.flag_chunk(chunk, document_id)
                all_flags.extend(semantic_flags)

        # Persist flags
        for flag in all_flags:
            record = ReviewFlagRecord(
                document_id=document_id,
                chunk_id=flag.source_chunk_id if flag.source_chunk_id != "N/A" else None,
                category=flag.category.value,
                severity=flag.severity.value,
                reason=flag.reason,
                source_page=flag.source_page,
                source_clause=flag.source_clause,
                extracted_value=flag.extracted_value,
                is_rule_based=flag.is_rule_based,
            )
            db.add(record)

        db.commit()

        # Build response summary
        high_count = sum(1 for f in all_flags if f.severity == FlagSeverity.HIGH)
        medium_count = sum(1 for f in all_flags if f.severity == FlagSeverity.MEDIUM)
        low_count = sum(1 for f in all_flags if f.severity == FlagSeverity.LOW)

        return ReviewFlagsResponse(
            document_id=str(document_id),
            flags=all_flags,
            total_flags=len(all_flags),
            high_severity_count=high_count,
            medium_severity_count=medium_count,
            low_severity_count=low_count,
        )

    def get_document_flags(
        self,
        document_id: UUID,
        db: Session,
    ) -> ReviewFlagsResponse:
        """Retrieve previously generated flags for a document."""
        records = (
            db.query(ReviewFlagRecord)
            .filter(ReviewFlagRecord.document_id == document_id)
            .all()
        )

        flags = [
            ReviewFlag(
                category=r.category,
                severity=r.severity,
                reason=r.reason,
                source_page=r.source_page,
                source_clause=r.source_clause,
                source_chunk_id=str(r.chunk_id) if r.chunk_id else "N/A",
                extracted_value=r.extracted_value,
                is_rule_based=r.is_rule_based,
            )
            for r in records
        ]

        high_count = sum(1 for f in flags if f.severity == FlagSeverity.HIGH)
        medium_count = sum(1 for f in flags if f.severity == FlagSeverity.MEDIUM)
        low_count = sum(1 for f in flags if f.severity == FlagSeverity.LOW)

        return ReviewFlagsResponse(
            document_id=str(document_id),
            flags=flags,
            total_flags=len(flags),
            high_severity_count=high_count,
            medium_severity_count=medium_count,
            low_severity_count=low_count,
        )
