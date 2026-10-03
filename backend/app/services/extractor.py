from typing import Optional
from app.services.llm.base import LLMProvider
from app.models.extraction import ExtractionResult, ExtractedEntity


class EntityExtractor:
    """
    Extract structured entities from legal text.
    Targets: dates, amounts, notice periods, payment terms, obligations, penalties, parties.
    """

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def extract(
        self,
        text: str,
        page_number: int,
        chunk_id: str,
    ) -> ExtractionResult:
        """
        Extract entities from text chunk.
        Returns all entities with source references.
        """
        system_prompt = """You are a legal document expert. Extract structured information from the provided text.

Be conservative: only extract information explicitly present in the text.
For each extracted entity, provide:
- field_name: type of entity (notice_period, payment_amount, party_name, effective_date, termination_condition, etc.)
- value: the extracted value

Return JSON with array of extracted entities."""

        user_prompt = f"""Extract all important entities from this legal text:

Text:
{text}

Source page: {page_number}
Source chunk: {chunk_id}

Return JSON matching this schema:
{{
    "entities": [
        {{"field_name": "entity_type", "value": "extracted_value"}},
        ...
    ]
}}

Be thorough but only extract explicit information."""

        try:
            # Define a minimal schema for extraction
            from pydantic import BaseModel, Field

            class EntityList(BaseModel):
                entities: list[dict] = Field(default_factory=list)

            result_dict = self.llm.call_with_schema(
                prompt=user_prompt,
                schema=EntityList,
                system_prompt=system_prompt,
            )

            # Convert to ExtractedEntity objects with source refs
            entities = []
            for entity_dict in result_dict.get("entities", []):
                entities.append(
                    ExtractedEntity(
                        field_name=entity_dict.get("field_name", "unknown"),
                        value=entity_dict.get("value", ""),
                        page_number=page_number,
                        chunk_id=chunk_id,
                    )
                )

            return ExtractionResult(
                entities=entities,
                raw_extraction=str(result_dict),
            )
        except Exception as e:
            # Return empty result on error
            return ExtractionResult(
                entities=[],
                raw_extraction=f"Extraction failed: {str(e)}",
            )
