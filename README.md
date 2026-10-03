# LegalLens

An AI-assisted legal document analysis system that helps users understand contracts and agreements.

## What It Does

LegalLens is **not** a legal advisor. It helps you **understand** documents by:

- **Extracting clauses** and classifying them (Payment, Termination, Confidentiality, etc.)
- **Extracting structured information** (dates, notice periods, amounts, obligations)
- **Flagging noteworthy clauses** for human review (not legal verdicts)
- **Answering questions** about documents with citations to source text
- **Comparing two versions** to identify changes at the clause level
- **Providing a simple web interface** and REST API

## What It Does NOT Do

- Provide legal advice
- Determine if a contract is valid or enforceable
- Make binding interpretations
- Replace a lawyer

**This is an educational prototype.**

## Technology Stack

### Backend
- Python 3.11+ / FastAPI
- Pydantic, SQLAlchemy, PostgreSQL + pgvector
- PyMuPDF for PDF processing
- sentence-transformers for embeddings
- BM25 for lexical retrieval
- OpenAI API for LLM-powered extraction and QA

### Frontend
- React + TypeScript + Vite

### Testing
- pytest, FastAPI TestClient
- Small evaluation dataset for metrics

### Infrastructure
- Docker Compose (PostgreSQL + pgvector)
- .env for secrets

## Architecture

High-level flow:

```
User uploads PDF
    ↓
PyMuPDF extracts text (preserves page numbers)
    ↓
Intelligent chunking (respects sections/paragraphs)
    ↓
Clauses extracted & classified (LLM + validation)
    ↓
Embeddings generated + stored
    ↓
User asks question
    ↓
Hybrid retrieval (BM25 + semantic)
    ↓
LLM generates answer with citations
```

See `docs/ARCHITECTURE.md` for detailed diagrams and flows.

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (or Docker + Docker Compose)
- OpenAI API key

### Setup

1. Clone and navigate:
```bash
cd LegalLens
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

4. Set up .env:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key and database URL
```

5. Start PostgreSQL (Docker):
```bash
docker-compose up -d
```

6. Run migrations:
```bash
cd backend
alembic upgrade head
```

7. Start backend:
```bash
cd backend
uvicorn app.main:app --reload
```

8. Start frontend:
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `POST /documents` — Upload a PDF
- `GET /documents/{document_id}` — Get document metadata
- `POST /documents/{document_id}/analyze` — Extract clauses and entities
- `GET /documents/{document_id}/clauses` — List extracted clauses
- `GET /documents/{document_id}/flags` — List risk flags
- `POST /documents/{document_id}/query` — Ask a question (RAG)
- `POST /documents/compare` — Compare two documents

See `docs/API.md` for full details.

## Evaluation

The project includes:
- **Retrieval evaluation**: Recall@k, Precision@k (BM25 vs embeddings vs hybrid)
- **Classification evaluation**: Accuracy, macro F1
- **Extraction evaluation**: Field-level exact match
- **QA evaluation**: Answer correctness, citation accuracy

See `docs/EVALUATION.md` for methodology and results.

## Limitations

- No OCR (text extraction from scanned PDFs)
- No user authentication
- Not suitable for production legal use
- Depends on LLM quality and may hallucinate
- Limited to English documents
- Small evaluation dataset

## Future Improvements

- OCR support
- Fine-tuned models for legal domain
- Multi-document analysis
- Real legal research integration
- User authentication
- Cloud deployment

## License

Educational use only.
