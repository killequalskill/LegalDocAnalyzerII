"""
Evaluation dataset for LegalLens.

Small curated set of legal documents with:
- Ground truth clause types
- Ground truth extracted entities
- Query-relevance mappings for retrieval evaluation
- Expected answers for Q&A evaluation
"""

# Sample evaluation data
EVALUATION_QUERIES = [
    {
        "query": "What is the payment amount?",
        "document": "sample_contract_1",
        "relevant_chunk_ids": ["chunk_1", "chunk_3"],
        "expected_answer_keywords": ["10000", "annual", "payment"],
        "should_have_sufficient_evidence": True,
    },
    {
        "query": "What are the termination rights?",
        "document": "sample_contract_1",
        "relevant_chunk_ids": ["chunk_5", "chunk_6"],
        "expected_answer_keywords": ["terminate", "30 days", "notice"],
        "should_have_sufficient_evidence": True,
    },
    {
        "query": "What is the renewal policy?",
        "document": "sample_contract_2",
        "relevant_chunk_ids": ["chunk_12"],
        "expected_answer_keywords": ["renew", "automatic", "year"],
        "should_have_sufficient_evidence": True,
    },
    {
        "query": "Are there confidentiality obligations?",
        "document": "sample_contract_1",
        "relevant_chunk_ids": ["chunk_8"],
        "expected_answer_keywords": ["confidential", "information"],
        "should_have_sufficient_evidence": False,  # Not in sample doc
    },
]

GROUND_TRUTH_CLAUSES = [
    {
        "document": "sample_contract_1",
        "chunk_id": "chunk_1",
        "expected_type": "payment",
        "text_contains": ["payment", "10000"],
    },
    {
        "document": "sample_contract_1",
        "chunk_id": "chunk_5",
        "expected_type": "termination",
        "text_contains": ["terminate", "30 days"],
    },
    {
        "document": "sample_contract_1",
        "chunk_id": "chunk_8",
        "expected_type": "confidentiality",
        "text_contains": ["confidential"],
    },
]

GROUND_TRUTH_ENTITIES = [
    {
        "document": "sample_contract_1",
        "chunk_id": "chunk_1",
        "field_name": "payment_amount",
        "expected_value": "10000",
    },
    {
        "document": "sample_contract_1",
        "chunk_id": "chunk_5",
        "field_name": "notice_period",
        "expected_value": "30 days",
    },
]
