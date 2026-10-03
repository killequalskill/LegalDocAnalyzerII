"""
Retrieval Evaluation

This module contains functions to evaluate retrieval quality on a small dataset.
Metrics: Recall@k, Precision@k, Mean Reciprocal Rank (MRR)
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class RetrievalEvalResult:
    """Evaluation metrics for a single query."""
    query: str
    recall_at_5: float
    recall_at_10: float
    precision_at_5: float
    precision_at_10: float
    mrr: float


def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int = 5) -> float:
    """
    Recall@k: proportion of relevant items in top-k results.
    recall = |retrieved ∩ relevant| / |relevant|
    """
    if not relevant_ids:
        return 0.0

    retrieved_at_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    intersection = retrieved_at_k & relevant_set

    return len(intersection) / len(relevant_set)


def precision_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int = 5) -> float:
    """
    Precision@k: proportion of retrieved items that are relevant.
    precision = |retrieved ∩ relevant| / k
    """
    if k == 0:
        return 0.0

    retrieved_at_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    intersection = retrieved_at_k & relevant_set

    return len(intersection) / k


def mean_reciprocal_rank(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
    """
    MRR: average of reciprocal ranks of first relevant item.
    mrr = 1 / rank_of_first_relevant
    Returns 0 if no relevant item found.
    """
    relevant_set = set(relevant_ids)

    for rank, item_id in enumerate(retrieved_ids, 1):
        if item_id in relevant_set:
            return 1.0 / rank

    return 0.0


def evaluate_retrieval(
    query: str,
    retrieved_ids: List[str],
    relevant_ids: List[str],
) -> RetrievalEvalResult:
    """
    Evaluate retrieval quality for a single query.
    """
    return RetrievalEvalResult(
        query=query,
        recall_at_5=recall_at_k(retrieved_ids, relevant_ids, k=5),
        recall_at_10=recall_at_k(retrieved_ids, relevant_ids, k=10),
        precision_at_5=precision_at_k(retrieved_ids, relevant_ids, k=5),
        precision_at_10=precision_at_k(retrieved_ids, relevant_ids, k=10),
        mrr=mean_reciprocal_rank(retrieved_ids, relevant_ids),
    )


def average_metrics(results: List[RetrievalEvalResult]) -> Dict[str, float]:
    """
    Compute average metrics across multiple queries.
    """
    if not results:
        return {}

    return {
        "avg_recall_at_5": sum(r.recall_at_5 for r in results) / len(results),
        "avg_recall_at_10": sum(r.recall_at_10 for r in results) / len(results),
        "avg_precision_at_5": sum(r.precision_at_5 for r in results) / len(results),
        "avg_precision_at_10": sum(r.precision_at_10 for r in results) / len(results),
        "avg_mrr": sum(r.mrr for r in results) / len(results),
    }
