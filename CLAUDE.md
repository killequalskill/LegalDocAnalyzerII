# LegalLens Development Guide

## Project Overview

LegalLens is an AI-assisted legal document analysis system. It helps users understand legal documents by extracting clauses, classifying them, identifying noteworthy sections, and answering questions using retrieval-augmented generation (RAG).

**What it does NOT do:**
- Provide legal advice
- Determine if a contract is legally valid
- Make binding judgments about enforceability

**What it DOES do:**
- Extract and classify important clauses (Payment, Termination, Confidentiality, etc.)
- Extract structured information (dates, notice periods, obligations)
- Flag potentially noteworthy clauses for human review
- Answer questions about documents with citations
- Compare two versions of a document
- Provide a simple web interface + REST API

## Key Design Principles

1. **Correctness over features**: Every extracted value must be traceable to source text.
2. **Explainability**: Decisions must be understandable. Show work, cite sources.
3. **Clean architecture**: Separate concerns—API, database, document processing, retrieval, LLM, business logic.
4. **Measurable evaluation**: Not "it works"—measure retrieval precision/recall, classification accuracy, etc.
5. **Realistic scope**: No OCR, fine-tuning, authentication, or production deployment initially.

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **Pydantic** for request/response validation
- **SQLAlchemy** for ORM
- **PostgreSQL** with pgvector for vector storage

### Document Processing
- **PyMuPDF** for PDF text extraction with page tracking
- **Page-aware chunking** that respects paragraph/section boundaries
- Design extensible for OCR (not implemented)

### NLP / Retrieval
- **sentence-transformers** for semantic embeddings
- **BM25** for lexical retrieval
- **Hybrid retrieval** combining both (with clear scoring strategy)
- Reranking only if measurably useful

### LLM Integration
- **OpenAI SDK** (abstracted so provider can be swapped)
- Structured output via Pydantic schemas
- Mock provider for testing
- No hard-coded provider logic throughout codebase

### Frontend
- **React** + **TypeScript** + **Vite**
- Simple, functional UI (not elaborate CSS)

### Testing
- **pytest** for backend
- **FastAPI TestClient** for API tests
- Unit tests for core logic
- Integration tests for workflows
- Small evaluation dataset for retrieval/extraction/QA

### Infrastructure
- **Docker Compose** for PostgreSQL + pgvector
- **.env** for secrets (never committed)
- **.env.example** with variable names only

## Project Structure

```
LegalLens/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── documents.py
│   │   │   │   ├── analysis.py
│   │   │   │   ├── search.py
│   │   │   │   └── comparison.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── db/
│   │   │   ├── models.py
│   │   │   ├── session.py
│   │   │   └── repositories/
│   │   ├── models/
│   │   │   ├── schemas.py
│   │   │   ├── clauses.py
│   │   │   └── documents.py
│   │   ├── services/
│   │   │   ├── document_parser.py
│   │   │   ├── chunker.py
│   │   │   ├── clause_classifier.py
│   │   │   ├── extractor.py
│   │   │   ├── embeddings.py
│   │   │   ├── retriever.py
│   │   │   ├── llm.py
│   │   │   ├── analyzer.py
│   │   │   └── comparator.py
│   │   └── main.py
│   └── tests/
│       ├── unit/
│       └── integration/
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── types/
│       └── App.tsx
├── data/
│   ├── sample_documents/
│   └── evaluation/
├── scripts/
├── docker-compose.yml
├── .env.example
├── README.md
└── CLAUDE.md
```

## Development Workflow

### Milestones (in order)

0. **Repository inspection and architecture** ✓ (current)
   - Set up project structure
   - Create CLAUDE.md, README skeleton, .gitignore

1. **Backend foundation**
   - FastAPI app, config, database connection
   - SQLAlchemy models
   - Health endpoint + test infrastructure

2. **PDF ingestion**
   - Document upload endpoint
   - PyMuPDF parser with page tracking
   - Intelligent chunking
   - Persistence

3. **Clause classification + extraction**
   - Pydantic schemas for clauses and entities
   - LLM abstraction (real + mock providers)
   - Structured classification and extraction
   - Tests with mocked LLM

4. **Retrieval**
   - Embeddings service
   - BM25 retrieval
   - Vector search
   - Hybrid ranking
   - Retrieval evaluation on small dataset

5. **RAG Question Answering**
   - Query endpoint
   - Retrieve → Answer → Cite workflow
   - Citation accuracy
   - Handle insufficient evidence

6. **Risk/review analysis**
   - Deterministic flagging rules
   - LLM-assisted semantic analysis where justified
   - Structured review flags

7. **Document comparison**
   - Clause-level diff
   - Changed values/dates
   - Added/removed/modified clauses

8. **React frontend**
   - Upload, overview, clauses, flags, Q&A, citations, comparison

9. **Evaluation + polish**
   - Evaluation dataset and metrics
   - Retrieval: Recall@k, Precision@k
   - Classification: accuracy, F1
   - Extraction: field-level exact match
   - QA: answer + citation correctness
   - Compare BM25 vs vector vs hybrid
   - Fix issues, improve README

10. **Interview preparation**
    - Create docs/INTERVIEW.md
    - Explain architecture, tradeoffs, limitations
    - Only include what was actually implemented

## Important Rules

### Git
- DO NOT commit, push, create branches, or modify history
- Only use `git status` and `git diff` to inspect changes
- All work remains uncommitted in working tree

### Development
- Work milestone-by-milestone, stop after each
- Explain what you're building before implementing
- Inspect existing code before adding
- Run tests/lint/type checks
- Fix errors
- Summarize what changed and why
- Stop and wait for approval before next milestone

### Interview Focus
- Never implement just to "use a technology"
- Understand everything you build:
  - How it works
  - Why it was chosen
  - Its limitations
  - Alternatives considered
  - How it was tested
- Document tradeoffs
- Be honest about weaknesses

### Code Style
- Clean, readable Python
- Type important functions
- Use Pydantic for validation
- Small functions
- Comments only for non-obvious reasoning
- No premature optimization
- Centralized configuration
- Explicit error handling

## Security & Privacy

- Never log full document contents
- Never log API keys
- Don't commit uploaded documents
- Validate file types and sizes
- Separate demo data from user uploads
- Note in README: educational prototype, not legal advice

## When You Get Stuck

1. Diagnose root cause rather than incremental patching
2. If an approach fails twice, try fundamentally different approach
3. Explain the deviation and confirm before proceeding
4. Be persistent and explore different tracks
