from typing import Optional
from app.services.llm.base import LLMProvider
from app.models.clauses import ClauseType, CLAUSE_DESCRIPTIONS
from app.models.extraction import ClauseClassificationResult


class ClauseClassifier:
    """
    Classify text chunks into clause types.
    Uses LLM with structured output via schema constraint.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def classify(self, text: str) -> ClauseClassificationResult:
        """
        Classify a text chunk into one of the predefined clause types.
        """
        # Build clause descriptions for the prompt
        clause_options = "\n".join([
            f"- {ct.value}: {CLAUSE_DESCRIPTIONS[ct]}"
            for ct in ClauseType
        ])

        system_prompt = """You are a legal document expert. Classify the given text into one of the provided clause types.

Be precise and conservative. Only classify if the text clearly matches the clause type.
For ambiguous cases, use "other"."""

        user_prompt = f"""Classify this text into one of these clause types:

{clause_options}

Text to classify:
{text}

Respond with JSON matching this schema:
{{
    "clause_type": "one of the above clause type values",
    "reasoning": "brief explanation for this classification",
    "confidence": null or a float between 0 and 1 if you can estimate it
}}"""

        try:
            result_dict = self.llm.call_with_schema(
                prompt=user_prompt,
                schema=ClauseClassificationResult,
                system_prompt=system_prompt,
            )

            return ClauseClassificationResult(**result_dict)
        except Exception as e:
            # Fallback on error
            return ClauseClassificationResult(
                clause_type=ClauseType.OTHER,
                reasoning=f"Classification failed: {str(e)}",
                confidence=None,
            )
