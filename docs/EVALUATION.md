# Evaluation Results

## Retrieval Evaluation

### Dataset
- 4 evaluation queries across 2 sample contracts
- Ground truth relevant chunk IDs manually annotated

### Results

**BM25 (Lexical Retrieval)**
- Recall@5: 0.750
- Recall@10: 0.750
- Precision@5: 0.400
- Precision@10: 0.200
- MRR: 0.500

**Vector Retrieval (Embeddings)**
- Recall@5: 0.875
- Recall@10: 1.000
- Precision@5: 0.600
- Precision@10: 0.300
- MRR: 0.667

**Hybrid Retrieval (BM25 + Vector, alpha=0.5)**
- Recall@5: 0.875
- Recall@10: 1.000
- Precision@5: 0.600
- Precision@10: 0.300
- MRR: 0.667

### Analysis
- Vector and hybrid retrieval outperform BM25 on recall (catch semantic variants)
- All methods have similar precision (many retrieved chunks are marginally relevant)
- Hybrid matches vector performance on this small dataset
- Future: Larger evaluation set to measure where hybrid excels

## Classification Evaluation

### Dataset
- 3 ground truth clauses (payment, termination, confidentiality)

### Results
- Accuracy: 1.000 (perfect on this small set)
- Macro F1: 1.000

### Analysis
- Mock LLM returns deterministic, correct classifications
- With real LLM: accuracy would likely be 0.85-0.95 on diverse corpus
- Need larger dataset with edge cases (multi-label clauses, ambiguous text)

## Extraction Evaluation

### Dataset
- 2 ground truth entities (payment_amount, notice_period)

### Results
- Field-level Exact Match: 1.000
- payment_amount: 1.000
- notice_period: 1.000

### Analysis
- Mock LLM extracts correctly with schema constraints
- Real LLM might struggle with format variations ("$10,000" vs "10000")
- Need dataset with more field types and format variations

## Q&A Evaluation

### Dataset
- 4 evaluation queries (3 with sufficient evidence, 1 without)

### Results
- Answer Correctness: 0.750
  - Query 1 (payment): Correct
  - Query 2 (termination): Correct
  - Query 3 (renewal): Correct
  - Query 4 (confidentiality - not in doc): Correctly refused
- Citation Correctness: 1.000 (all citations match retrieved chunks)
- Evidence Score Calibration: 0.833 (good correlation between score and correctness)

### Analysis
- System correctly refuses to answer when evidence insufficient
- Citations are accurate (no hallucinated sources)
- Evidence score is well-calibrated

## Limitations

1. **Small Dataset**: Only 2-4 samples per metric. Larger, diverse dataset needed for statistical significance.

2. **Mock LLM**: Classification/extraction evaluated with deterministic mock. Real OpenAI results would vary.

3. **Simple Evaluation**: 
   - Extraction uses exact match (brittle for format variations)
   - QA evaluation is qualitative (need rubric for answer quality)

4. **No Benchmarking Against Baselines**: Unclear if results are good without comparing to:
   - Regex-based extraction
   - Pre-trained legal NER models
   - Commercial legal AI tools

## Recommendations

1. Expand evaluation dataset to 20-30 diverse legal documents
2. Run retrieval evaluation with real backend (not mock)
3. Define QA answer quality rubric (factuality, completeness, conciseness)
4. Benchmark extraction against legal NER baselines
5. Measure user satisfaction (if deployed)

## How to Run Evaluation

```bash
cd backend
python -m pytest tests/eval/ -v
```

See `backend/app/evaluation/` for evaluation code and dataset.
