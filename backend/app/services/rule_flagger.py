from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import DocumentChunk
from app.db.clause_models import ExtractedEntity, Clause
from app.models.flags import ReviewFlag, FlagCategory, FlagSeverity
from app.models.clauses import ClauseType


class RuleBasedFlagger:
    """
    Deterministic rule-based flagging.
    Checks for common issues without calling LLM.
    """

    # Rules: notice periods shorter than this are flagged
    MINIMUM_NOTICE_DAYS = 30

    # Rules: payment amounts significantly lower are unusual
    EXPECTED_PAYMENT_RANGE = (5000, 500000)  # USD

    def __init__(self):
        pass

    def flag_document(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[ReviewFlag]:
        """
        Apply deterministic rules to document.
        Returns list of flags.
        """
        flags = []

        # Check for missing critical clauses
        flags.extend(self._check_missing_clauses(document_id, db))

        # Check for unusual extracted values
        flags.extend(self._check_unusual_values(document_id, db))

        # Check for asymmetric terms
        flags.extend(self._check_asymmetric_terms(document_id, db))

        return flags

    def _check_missing_clauses(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[ReviewFlag]:
        """Flag if critical clauses are missing."""
        flags = []

        # Get all clause types in document
        clauses = (
            db.query(Clause)
            .filter(Clause.document_id == document_id)
            .all()
        )

        clause_types = {c.clause_type for c in clauses}

        # List of critical clauses that should be present
        critical_clauses = [
            ClauseType.PAYMENT,
            ClauseType.TERMINATION,
            ClauseType.GOVERNING_LAW,
        ]

        for critical in critical_clauses:
            if critical.value not in clause_types:
                flags.append(
                    ReviewFlag(
                        category=FlagCategory.MISSING_CLAUSE,
                        severity=FlagSeverity.HIGH,
                        reason=f"Critical clause missing: {critical.value.replace('_', ' ').title()}. "
                               f"This is typically present in contracts.",
                        source_page=1,  # Unknown page for missing clause
                        source_chunk_id="N/A",
                        extracted_value=None,
                        is_rule_based=True,
                    )
                )

        return flags

    def _check_unusual_values(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[ReviewFlag]:
        """Flag unusual extracted values (amounts, dates, etc.)."""
        flags = []

        entities = (
            db.query(ExtractedEntity)
            .filter(ExtractedEntity.document_id == document_id)
            .all()
        )

        for entity in entities:
            # Check payment amounts
            if entity.field_name == "payment_amount":
                try:
                    # Try to extract numeric value
                    import re
                    amount_str = re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', entity.value)
                    if amount_str:
                        amount = float(amount_str[0].replace(",", ""))
                        if amount < self.EXPECTED_PAYMENT_RANGE[0]:
                            flags.append(
                                ReviewFlag(
                                    category=FlagCategory.UNUSUAL_AMOUNT,
                                    severity=FlagSeverity.MEDIUM,
                                    reason=f"Payment amount appears unusually low: {entity.value}. "
                                           f"Verify this is intentional.",
                                    source_page=entity.page_number,
                                    source_chunk_id=str(entity.chunk_id),
                                    extracted_value=entity.value,
                                    is_rule_based=True,
                                )
                            )
                except Exception:
                    pass

            # Check notice periods
            if entity.field_name == "notice_period":
                try:
                    import re
                    days_match = re.search(r'(\d+)\s*days?', entity.value, re.IGNORECASE)
                    if days_match:
                        days = int(days_match.group(1))
                        if days < self.MINIMUM_NOTICE_DAYS:
                            flags.append(
                                ReviewFlag(
                                    category=FlagCategory.SHORT_NOTICE_PERIOD,
                                    severity=FlagSeverity.MEDIUM,
                                    reason=f"Notice period is short: {entity.value}. "
                                           f"This may not provide adequate time to respond.",
                                    source_page=entity.page_number,
                                    source_chunk_id=str(entity.chunk_id),
                                    extracted_value=entity.value,
                                    is_rule_based=True,
                                )
                            )
                except Exception:
                    pass

        return flags

    def _check_asymmetric_terms(
        self,
        document_id: UUID,
        db: Session,
    ) -> List[ReviewFlag]:
        """Flag asymmetric obligations between parties."""
        flags = []

        # Check for automatic renewal
        clauses = (
            db.query(Clause)
            .filter(
                Clause.document_id == document_id,
                Clause.clause_type == ClauseType.RENEWAL.value,
            )
            .all()
        )

        for clause in clauses:
            if "automatic" in clause.reasoning.lower():
                flags.append(
                    ReviewFlag(
                        category=FlagCategory.AUTO_RENEWAL,
                        severity=FlagSeverity.MEDIUM,
                        reason="Agreement has automatic renewal. Review termination notice "
                               "requirements to ensure you don't miss renewal deadlines.",
                        source_page=1,  # Would need to retrieve from chunk
                        source_clause=None,
                        source_chunk_id=str(clause.chunk_id),
                        extracted_value="Automatic renewal detected",
                        is_rule_based=True,
                    )
                )

        return flags
