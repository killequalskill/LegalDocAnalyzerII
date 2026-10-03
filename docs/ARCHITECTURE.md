# LegalLens Architecture & Design

## System Overview

```
User
  ↓
Frontend (React)
  ↓
FastAPI Backend
  ↓
[Services Layer]
  ├─ Document Parser (PyMuPDF)
  ├─ Chunker (hierarchical, respects sections)
  ├─ Clause Classifier (LLM-based)
  ├─ Entity Extractor (LLM-based)
  ├─ Risk Flagger (rules + semantic)
  ├─ Embeddings (sentence-transformers)
  ├─ Retriever (BM25 + vector + hybrid)
  └─ QA Service (RAG)
  ↓
[Data Layer]
  ├─ PostgreSQL
  ├─ pgvector
  └─ SQLAlchemy ORM
```

## Key Design Decisions

### 1. Document Processing

**Chunking Strategy**: Hierarchical, section-aware
- Detects section headings (PAYMENT, TERMINATION, etc.)
- Respects paragraph boundaries
- Token-aware sizing (300-2000 tokens, target 800)
- Preserves: page number, section name, clause ID, character offsets

**Why**: Legal documents have explicit structure. Respecting it keeps clauses whole and citable.

### 2. Information Extraction

**LLM Abstraction**:
- Abstract interface (`LLMProvider`) with two methods: `call()` and `call_with_schema()`
- Real provider: OpenAI with JSON schema constraints
- Mock provider: Deterministic for testing

**Why**: Vendor lock-in risk mitigation. Can swap providers without touching business logic.

**Structured Output**:
- All LLM outputs validated via Pydantic schemas
- Schema-constrained output (JSON mode) enforces structure
- Fails fast if LLM response doesn't match schema

**Why**: Prevents garbage-in-garbage-out. If LLM can't follow the schema, better to error than hallucinate.

### 3. Retrieval

**Three Methods**:
- **BM25**: Keyword-based, fast, interpretable
- **Vector**: Semantic embeddings, catches paraphrases
- **Hybrid**: Weighted combination (alpha=0.5 by default)

**Why**: Legal docs benefit from both keyword precision and semantic understanding. Hybrid often best of both.

**Evaluation**:
- Recall@k: Did we find the relevant documents?
- Precision@k: Were the results we found relevant?
- MRR: How high-ranked was the first relevant result?

### 4. Risk Flagging

**Separation of Concerns**:
- **Facts**: "Payment is $10,000" (extracted)
- **Observations**: "This is unusually low" (rule-based flag)
- **Legal Knowledge**: "Contracts usually require X" (never claimed as truth)

**Rule-Based + Semantic**:
- Rules run always (fast, interpretable)
- Semantic (LLM) runs optionally (nuanced, slower)
- Each flag marked as `is_rule_based` (true/false)

**Why**: Rules are trustworthy. LLM adds nuance but can hallucinate. Users need to know the source.

### 5. Question Answering

**RAG (Retrieval-Augmented Generation)**:
- Retrieve top-k relevant chunks
- Evaluate evidence quality (avg score > 0.6, minimum 2 chunks)
- If sufficient: generate answer with LLM
- If insufficient: refuse to answer

**Why**: Grounding answers in retrieved evidence reduces hallucination. Refusing to answer builds trust.

**Citations**:
- Every answer includes source page, section, clause ID, excerpt
- Enables user verification

**Why**: Legal domain demands trust. Citations prove the answer isn't made up.

### 6. Data Models

**Core Entities**:
- `Document`: Metadata, extraction timestamps
- `DocumentChunk`: Text + source metadata (page, section, clause)
- `Clause`: Classification result with reasoning, confidence
- `ExtractedEntity`: Extracted value with source reference
- `ReviewFlag`: Risk flag with category, severity, reason
- `DocumentEmbedding`: Vector embedding with chunk reference

**Why**: Full traceability. Every extracted/classified/flagged value references its source.

## Technology Stack Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python | Industry standard for NLP, LLM integration |
| Framework | FastAPI | Modern, fast, automatic OpenAPI docs, type hints |
| ORM | SQLAlchemy | Flexible, no vendor lock-in, mature |
| Database | PostgreSQL | Reliable, pgvector extension for embeddings |
| Embeddings | sentence-transformers | Fast (runs on CPU), good quality, pre-trained on technical text |
| Lexical | rank-bm25 | Simple, no external index needed |
| LLM | OpenAI | Best-in-class models, JSON schema support, affordable |
| Frontend | React + Vite | Modern UX, simple tooling, fast dev experience |

## Known Limitations

1. **No OCR**: Can't process scanned PDFs
2. **English-only**: Embeddings and LLM tuned for English
3. **No fine-tuning**: Uses pre-trained models, not domain-specific
4. **Single document**: Can't compare across multiple documents (yet)
5. **No real-time updates**: Embeddings static after upload
6. **Small evaluation dataset**: Results on 2-4 sample documents
7. **Mock LLM in tests**: Classification/extraction tested with deterministic mock, not real OpenAI

## Future Improvements

1. **OCR Support**: Add Tesseract or commercial OCR for scanned documents
2. **Multi-document Analysis**: Compare terms across multiple contracts
3. **Fine-tuning**: Domain-specific legal models for better extraction
4. **Real-time**: Stream answer generation, incremental results
5. **Confidence Learning**: Train model to predict which flags are useful
6. **Fuzzy Matching**: Better clause matching when numbering changes
7. **Semantic Similarity**: Fuzzy matching between similar clauses in v1 vs v2
