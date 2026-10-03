from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.models import DocumentChunk
from app.models.comparison import ClauseChange, ChangeType, ComparisonResponse
from difflib import SequenceMatcher


class DocumentComparator:
    """
    Compare two versions of a document.
    Matches clauses between versions and identifies changes.
    """

    # Similarity threshold for matching clauses (0-1)
    CLAUSE_MATCH_THRESHOLD = 0.6

    def compare_documents(
        self,
        doc_v1_id: UUID,
        doc_v2_id: UUID,
        db: Session,
    ) -> ComparisonResponse:
        """
        Compare two document versions.

        Strategy:
        1. Fetch all chunks from both versions
        2. Build mapping of clauses: section + clause_id
        3. For matching clauses: compare text
        4. For unmatched: flag as added/removed
        """
        # Fetch chunks from both documents
        chunks_v1 = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == doc_v1_id)
            .order_by(DocumentChunk.page_number, DocumentChunk.char_start)
            .all()
        )

        chunks_v2 = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == doc_v2_id)
            .order_by(DocumentChunk.page_number, DocumentChunk.char_start)
            .all()
        )

        if not chunks_v1 or not chunks_v2:
            return ComparisonResponse(
                document_v1_id=str(doc_v1_id),
                document_v2_id=str(doc_v2_id),
                total_changes=0,
                added_count=0,
                removed_count=0,
                modified_count=0,
                unchanged_count=0,
                changes=[],
            )

        # Build clause mappings
        clauses_v1 = self._build_clause_map(chunks_v1)
        clauses_v2 = self._build_clause_map(chunks_v2)

        # Compare
        changes = self._compare_clause_maps(clauses_v1, clauses_v2, chunks_v1, chunks_v2)

        # Count by type
        added = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
        removed = sum(1 for c in changes if c.change_type == ChangeType.REMOVED)
        modified = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)
        unchanged = sum(1 for c in changes if c.change_type == ChangeType.UNCHANGED)

        return ComparisonResponse(
            document_v1_id=str(doc_v1_id),
            document_v2_id=str(doc_v2_id),
            total_changes=len(changes),
            added_count=added,
            removed_count=removed,
            modified_count=modified,
            unchanged_count=unchanged,
            changes=changes,
        )

    def _build_clause_map(self, chunks: List) -> dict:
        """
        Build a map of clauses by (section_name, clause_id).
        Returns: {(section, clause_id): chunk}
        """
        clause_map = {}

        for chunk in chunks:
            key = (chunk.section_name or "Unlabeled", chunk.clause_id or "0")
            clause_map[key] = chunk

        return clause_map

    def _compare_clause_maps(
        self,
        clauses_v1: dict,
        clauses_v2: dict,
        chunks_v1: List,
        chunks_v2: List,
    ) -> List[ClauseChange]:
        """
        Compare two clause maps and identify changes.
        """
        changes = []
        matched_v2_keys = set()

        # Check v1 clauses against v2
        for key, chunk_v1 in clauses_v1.items():
            if key in clauses_v2:
                # Clause exists in both versions
                chunk_v2 = clauses_v2[key]
                matched_v2_keys.add(key)

                # Compare text
                similarity = self._text_similarity(chunk_v1.text, chunk_v2.text)

                if similarity > 0.95:
                    # Text is essentially the same
                    change_type = ChangeType.UNCHANGED
                    summary = f"Clause {key[1] if key[1] != '0' else key[0]} unchanged"
                else:
                    # Text changed
                    change_type = ChangeType.MODIFIED
                    summary = self._generate_modification_summary(chunk_v1.text, chunk_v2.text, key)

                changes.append(
                    ClauseChange(
                        change_type=change_type,
                        section_name=key[0],
                        clause_id=key[1] if key[1] != "0" else None,
                        v1_text=chunk_v1.text[:200],
                        v1_page=chunk_v1.page_number,
                        v1_chunk_id=str(chunk_v1.id),
                        v2_text=chunk_v2.text[:200],
                        v2_page=chunk_v2.page_number,
                        v2_chunk_id=str(chunk_v2.id),
                        summary=summary,
                    )
                )
            else:
                # Clause removed in v2
                summary = f"Removed: {key[0]}"
                if key[1] != "0":
                    summary += f" (Clause {key[1]})"

                changes.append(
                    ClauseChange(
                        change_type=ChangeType.REMOVED,
                        section_name=key[0],
                        clause_id=key[1] if key[1] != "0" else None,
                        v1_text=chunk_v1.text[:200],
                        v1_page=chunk_v1.page_number,
                        v1_chunk_id=str(chunk_v1.id),
                        summary=summary,
                    )
                )

        # Check for newly added clauses in v2
        for key, chunk_v2 in clauses_v2.items():
            if key not in matched_v2_keys:
                summary = f"Added: {key[0]}"
                if key[1] != "0":
                    summary += f" (Clause {key[1]})"

                changes.append(
                    ClauseChange(
                        change_type=ChangeType.ADDED,
                        section_name=key[0],
                        clause_id=key[1] if key[1] != "0" else None,
                        v2_text=chunk_v2.text[:200],
                        v2_page=chunk_v2.page_number,
                        v2_chunk_id=str(chunk_v2.id),
                        summary=summary,
                    )
                )

        return changes

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Compute text similarity as ratio of matching characters.
        Returns 0-1 where 1 is identical.
        """
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()

    def _generate_modification_summary(
        self,
        text_v1: str,
        text_v2: str,
        key: Tuple[str, str],
    ) -> str:
        """Generate human-readable summary of modification."""
        section, clause_id = key

        # Try to detect specific changes
        import re

        # Look for number changes (amounts, dates, percentages)
        numbers_v1 = set(re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', text_v1))
        numbers_v2 = set(re.findall(r'\d+(?:,\d{3})*(?:\.\d{2})?', text_v2))

        if numbers_v1 != numbers_v2:
            removed_nums = numbers_v1 - numbers_v2
            added_nums = numbers_v2 - numbers_v1
            if removed_nums and added_nums:
                return f"Modified: {section} - Value changed from {', '.join(removed_nums)} to {', '.join(added_nums)}"

        # Look for day/duration changes
        days_v1 = re.findall(r'(\d+)\s*days?', text_v1, re.IGNORECASE)
        days_v2 = re.findall(r'(\d+)\s*days?', text_v2, re.IGNORECASE)

        if days_v1 != days_v2:
            return f"Modified: {section} - Notice/duration changed from {' or '.join(days_v1)} to {' or '.join(days_v2)} days"

        # Generic modification
        return f"Modified: {section} - Text changed"
