"""
Evaluation metrics and benchmarking for LegalLens.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval evaluation."""
    method: str  # bm25, vector, hybrid
    recall_at_5: float
    recall_at_10: float
    precision_at_5: float
    precision_at_10: float
    mrr: float  # Mean Reciprocal Rank


@dataclass
class ClassificationMetrics:
    """Metrics for clause classification."""
    accuracy: float
    macro_f1: float
    per_class_f1: Dict[str, float]


@dataclass
class ExtractionMetrics:
    """Metrics for entity extraction."""
    field_level_exact_match: float
    by_field: Dict[str, float]


@dataclass
class QAMetrics:
    """Metrics for Q&A evaluation."""
    answer_correctness: float
    citation_correctness: float
    evidence_score_calibration: float


@dataclass
class BenchmarkResults:
    """Complete benchmark results."""
    retrieval: Dict[str, RetrievalMetrics]  # method -> metrics
    classification: ClassificationMetrics
    extraction: ExtractionMetrics
    qa: QAMetrics
    timestamp: str


class EvaluationFramework:
    """Framework for evaluating LegalLens."""

    def __init__(self):
        pass

    def evaluate_retrieval(
        self,
        retrieved_ids: List[str],
        relevant_ids: List[str],
        method: str,
    ) -> RetrievalMetrics:
        """
        Evaluate retrieval results.

        Metrics:
        - Recall@k: % of relevant items in top-k
        - Precision@k: % of retrieved items that are relevant
        - MRR: Rank of first relevant item
        """
        # Implementation uses existing retrieval_evaluation module
        from app.services.retrieval_evaluation import (
            recall_at_k,
            precision_at_k,
            mean_reciprocal_rank,
        )

        return RetrievalMetrics(
            method=method,
            recall_at_5=recall_at_k(retrieved_ids, relevant_ids, k=5),
            recall_at_10=recall_at_k(retrieved_ids, relevant_ids, k=10),
            precision_at_5=precision_at_k(retrieved_ids, relevant_ids, k=5),
            precision_at_10=precision_at_k(retrieved_ids, relevant_ids, k=10),
            mrr=mean_reciprocal_rank(retrieved_ids, relevant_ids),
        )

    def evaluate_classification(
        self,
        predictions: List[str],
        ground_truth: List[str],
    ) -> ClassificationMetrics:
        """
        Evaluate clause classification.

        Metrics:
        - Accuracy: % correct predictions
        - Macro F1: Average F1 across all classes
        """
        from sklearn.metrics import accuracy_score, f1_score, classification_report

        acc = accuracy_score(ground_truth, predictions)
        macro_f1 = f1_score(ground_truth, predictions, average='macro', zero_division=0)

        # Per-class F1
        report = classification_report(ground_truth, predictions, output_dict=True, zero_division=0)
        per_class_f1 = {k: v['f1-score'] for k, v in report.items() if k not in ['accuracy', 'macro avg', 'weighted avg']}

        return ClassificationMetrics(
            accuracy=acc,
            macro_f1=macro_f1,
            per_class_f1=per_class_f1,
        )

    def evaluate_extraction(
        self,
        extracted: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]],
    ) -> ExtractionMetrics:
        """
        Evaluate entity extraction.

        Metrics:
        - Field-level exact match: % of fields with correct values
        """
        # Build lookup: (document, field_name) -> expected_value
        expected = {}
        for item in ground_truth:
            key = (item["document"], item["field_name"])
            expected[key] = item["expected_value"].lower()

        # Check predictions
        correct = 0
        total = 0
        by_field = {}

        for item in extracted:
            key = (item["document"], item["field_name"])
            if key in expected:
                total += 1
                pred_value = item["value"].lower()
                expected_value = expected[key]

                # Simple exact match (could be more sophisticated)
                is_match = pred_value == expected_value or expected_value in pred_value

                if is_match:
                    correct += 1

                # Per-field tracking
                field = item["field_name"]
                if field not in by_field:
                    by_field[field] = {"correct": 0, "total": 0}
                by_field[field]["total"] += 1
                if is_match:
                    by_field[field]["correct"] += 1

        # Compute rates
        exact_match = correct / total if total > 0 else 0.0
        by_field_rates = {
            field: data["correct"] / data["total"] if data["total"] > 0 else 0.0
            for field, data in by_field.items()
        }

        return ExtractionMetrics(
            field_level_exact_match=exact_match,
            by_field=by_field_rates,
        )

    def generate_report(self, results: BenchmarkResults) -> str:
        """Generate a human-readable benchmark report."""
        report = []
        report.append("=" * 60)
        report.append("LEGALLENS EVALUATION REPORT")
        report.append("=" * 60)
        report.append("")

        # Retrieval
        report.append("RETRIEVAL EVALUATION")
        report.append("-" * 60)
        for method, metrics in results.retrieval.items():
            report.append(f"\nMethod: {method.upper()}")
            report.append(f"  Recall@5:    {metrics.recall_at_5:.3f}")
            report.append(f"  Recall@10:   {metrics.recall_at_10:.3f}")
            report.append(f"  Precision@5: {metrics.precision_at_5:.3f}")
            report.append(f"  Precision@10:{metrics.precision_at_10:.3f}")
            report.append(f"  MRR:         {metrics.mrr:.3f}")

        # Classification
        report.append("\n\nCLASSIFICATION EVALUATION")
        report.append("-" * 60)
        report.append(f"Accuracy:  {results.classification.accuracy:.3f}")
        report.append(f"Macro F1:  {results.classification.macro_f1:.3f}")
        if results.classification.per_class_f1:
            report.append("\nPer-class F1:")
            for class_name, f1 in results.classification.per_class_f1.items():
                report.append(f"  {class_name}: {f1:.3f}")

        # Extraction
        report.append("\n\nEXTRACTION EVALUATION")
        report.append("-" * 60)
        report.append(f"Field-level Exact Match: {results.extraction.field_level_exact_match:.3f}")
        if results.extraction.by_field:
            report.append("\nBy field:")
            for field, rate in results.extraction.by_field.items():
                report.append(f"  {field}: {rate:.3f}")

        # QA
        report.append("\n\nQ&A EVALUATION")
        report.append("-" * 60)
        report.append(f"Answer Correctness:       {results.qa.answer_correctness:.3f}")
        report.append(f"Citation Correctness:     {results.qa.citation_correctness:.3f}")
        report.append(f"Evidence Score Calib:     {results.qa.evidence_score_calibration:.3f}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)
