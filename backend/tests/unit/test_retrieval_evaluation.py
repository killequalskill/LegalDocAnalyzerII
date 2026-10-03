import pytest
from app.services.retrieval_evaluation import (
    recall_at_k,
    precision_at_k,
    mean_reciprocal_rank,
    evaluate_retrieval,
    average_metrics,
)


def test_recall_at_k():
    """Test Recall@k calculation."""
    retrieved = ["a", "b", "c", "d", "e"]
    relevant = ["a", "c", "e", "f"]

    # Top 5: {a, b, c, d, e} ∩ {a, c, e, f} = {a, c, e}
    # recall = 3 / 4 = 0.75
    assert recall_at_k(retrieved, relevant, k=5) == 0.75

    # Top 3: {a, b, c} ∩ {a, c, e, f} = {a, c}
    # recall = 2 / 4 = 0.5
    assert recall_at_k(retrieved, relevant, k=3) == 0.5


def test_precision_at_k():
    """Test Precision@k calculation."""
    retrieved = ["a", "b", "c", "d", "e"]
    relevant = ["a", "c", "e", "f"]

    # Top 5: {a, b, c, d, e} ∩ {a, c, e, f} = {a, c, e}
    # precision = 3 / 5 = 0.6
    assert precision_at_k(retrieved, relevant, k=5) == 0.6

    # Top 3: {a, b, c} ∩ {a, c, e, f} = {a, c}
    # precision = 2 / 3
    assert abs(precision_at_k(retrieved, relevant, k=3) - 2/3) < 0.01


def test_mrr():
    """Test Mean Reciprocal Rank."""
    # First relevant at position 2
    retrieved = ["x", "a", "b"]
    relevant = ["a", "b", "c"]
    assert mean_reciprocal_rank(retrieved, relevant) == 0.5  # 1/2

    # First relevant at position 1
    retrieved = ["a", "x", "y"]
    assert mean_reciprocal_rank(retrieved, relevant) == 1.0  # 1/1

    # No relevant found
    retrieved = ["x", "y", "z"]
    assert mean_reciprocal_rank(retrieved, relevant) == 0.0


def test_evaluate_retrieval():
    """Test full evaluation for single query."""
    retrieved = ["a", "b", "c", "d", "e"]
    relevant = ["a", "c", "e"]

    result = evaluate_retrieval("test query", retrieved, relevant)

    assert result.query == "test query"
    assert result.recall_at_5 == 1.0  # all relevant found
    assert result.precision_at_5 == 0.6  # 3/5
    assert result.mrr == 1.0  # first item is relevant


def test_average_metrics():
    """Test averaging across multiple queries."""
    from app.services.retrieval_evaluation import RetrievalEvalResult

    results = [
        RetrievalEvalResult("q1", 0.8, 0.9, 0.7, 0.8, 0.5),
        RetrievalEvalResult("q2", 0.6, 0.7, 0.5, 0.6, 0.3),
    ]

    avg = average_metrics(results)

    assert avg["avg_recall_at_5"] == 0.7  # (0.8 + 0.6) / 2
    assert avg["avg_precision_at_5"] == 0.6  # (0.7 + 0.5) / 2
    assert avg["avg_mrr"] == 0.4  # (0.5 + 0.3) / 2
