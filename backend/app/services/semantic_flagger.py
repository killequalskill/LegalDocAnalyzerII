from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.services.llm.base import LLMProvider
from app.models.flags import ReviewFlag, FlagCategory, FlagSeverity
from app.db.models import DocumentChunk
from pydantic import BaseModel, Field


class LLMFlagResult(BaseModel):
    """Result from LLM flag generation."""
    category: str
    severity: str
    reason: str
    extracted_value: Optional[str] = None


class SemanticFlagger:
    """
    LLM-based semantic flagging for complex issues.
    Used when deterministic rules are insufficient.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def flag_chunk(
        self,
        chunk: any,  # DocumentChunk
        document_id: UUID,
    ) -> List[ReviewFlag]:
        """
        Use LLM to identify semantic issues in a chunk.
        Only for complex analysis—deterministic rules preferred.
        """
        flags = []

        system_prompt = """You are a legal document reviewer. Analyze this clause for noteworthy issues that a human should review.

Do NOT provide legal advice. Instead, flag observations for human review.

Focus on:
- Unusual or vague obligations
- Asymmetric terms between parties
- Missing standard protections
- Ambiguous language that could lead to disputes

Return JSON with array of flags, or empty array if none found."""

        user_prompt = f"""Analyze this clause for potential issues:

PAGE: {chunk.page_number}
SECTION: {chunk.section_name}
CLAUSE: {chunk.clause_id}

TEXT:
{chunk.text}

Return JSON:
{{
    "flags": [
        {{"category": "flag_type", "severity": "low|medium|high", "reason": "observation"}},
        ...
    ]
}}"""

        try:
            from pydantic import BaseModel

            class FlagList(BaseModel):
                flags: list[dict] = Field(default_factory=list)

            result_dict = self.llm.call_with_schema(
                prompt=user_prompt,
                schema=FlagList,
                system_prompt=system_prompt,
            )

            for flag_dict in result_dict.get("flags", []):
                try:
                    category = FlagCategory(flag_dict.get("category", "other"))
                except ValueError:
                    category = FlagCategory.OTHER

                try:
                    severity = FlagSeverity(flag_dict.get("severity", "low"))
                except ValueError:
                    severity = FlagSeverity.LOW

                flags.append(
                    ReviewFlag(
                        category=category,
                        severity=severity,
                        reason=flag_dict.get("reason", ""),
                        source_page=chunk.page_number,
                        source_clause=chunk.clause_id,
                        source_chunk_id=str(chunk.id),
                        extracted_value=chunk.text[:100],
                        is_rule_based=False,
                    )
                )
        except Exception as e:
            # Fail gracefully—LLM-based flagging is optional
            pass

        return flags
