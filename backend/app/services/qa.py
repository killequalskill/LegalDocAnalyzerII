from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from app.services.llm.base import LLMProvider
from app.services.retriever import HybridRetriever
from app.services.embeddings import EmbeddingService
from app.models.qa import Citation, AnswerResponse


class RAGService:
    """
    Retrieval-Augmented Generation (RAG) for question answering.

    Pipeline:
    1. Retrieve relevant chunks from document
    2. Check evidence quality (top-k scores)
    3. If sufficient, generate answer with LLM
    4. Otherwise, refuse or hedge
    5. Attach citations and confidence
    """

    # Evidence quality thresholds
    STRONG_EVIDENCE_THRESHOLD = 0.6  # Average score > 0.6
    MINIMUM_RETRIEVAL_SCORE = 0.3  # No chunk below this
    MINIMUM_CHUNKS = 2  # At least 2 relevant chunks

    def __init__(
        self,
        llm_provider: LLMProvider,
        embedding_service: EmbeddingService = None,
    ):
        self.llm = llm_provider
        self.retriever = HybridRetriever(embedding_service or EmbeddingService())

    def answer_question(
        self,
        query: str,
        document_id: UUID,
        db: Session,
        top_k: int = 5,
        retrieval_method: str = "hybrid",
    ) -> AnswerResponse:
        """
        Answer a question about a document using RAG.
        """
        # Retrieve evidence
        results = self.retriever.retrieve(
            query=query,
            document_id=document_id,
            db=db,
            top_k=top_k,
            method=retrieval_method,
        )

        # Evaluate evidence quality
        evidence_score, notes = self._evaluate_evidence(results)
        has_sufficient_evidence = (
            evidence_score >= self.STRONG_EVIDENCE_THRESHOLD
            and len(results) >= self.MINIMUM_CHUNKS
        )

        # Generate answer
        if has_sufficient_evidence:
            answer_text = self._generate_answer(query, results)
        else:
            answer_text = self._generate_insufficient_evidence_response(query, notes)

        # Build citations from retrieved chunks
        citations = [
            Citation(
                page_number=r["page_number"],
                section_name=r["section_name"],
                clause_id=r["clause_id"],
                chunk_id=r["chunk_id"],
                text=r["text"][:200],  # Truncate for readability
            )
            for r in results
        ]

        return AnswerResponse(
            query=query,
            answer=answer_text,
            citations=citations,
            evidence_score=evidence_score,
            has_sufficient_evidence=has_sufficient_evidence,
            evidence_notes=notes,
        )

    def _evaluate_evidence(self, results: List[dict]) -> Tuple[float, str]:
        """
        Evaluate quality of retrieved evidence.

        Returns:
            (score: 0-1, notes: explanation)
        """
        if not results:
            return 0.0, "No relevant chunks found"

        scores = [r["score"] for r in results]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)

        notes = f"Retrieved {len(results)} chunks. "
        notes += f"Avg relevance: {avg_score:.2f}, Min: {min_score:.2f}"

        if min_score < self.MINIMUM_RETRIEVAL_SCORE:
            notes += f" (some chunks below threshold {self.MINIMUM_RETRIEVAL_SCORE})"

        return avg_score, notes

    def _generate_answer(self, query: str, results: List[dict]) -> str:
        """
        Generate answer using LLM with retrieved evidence.
        """
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[Section {i+1}, Page {r['page_number']}]\n{r['text']}"
            for i, r in enumerate(results)
        ])

        system_prompt = """You are a legal document assistant. Answer questions based on the provided document excerpts.

Rules:
- Only use information from the provided excerpts
- Be concise and precise
- If information is not in the excerpts, say so
- Distinguish between what the document explicitly states vs what you infer"""

        user_prompt = f"""Based on these document excerpts, answer the question:

EXCERPTS:
{context}

QUESTION:
{query}

ANSWER:"""

        try:
            response = self.llm.call(user_prompt, system_prompt=system_prompt)
            return response.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def _generate_insufficient_evidence_response(
        self,
        query: str,
        notes: str,
    ) -> str:
        """
        Generate response when evidence is insufficient.
        """
        return (
            f"I cannot answer this question with sufficient confidence. {notes}\n\n"
            f"To improve results for '{query}', the document may need more explicit information "
            "on this topic, or the question might be outside the document's scope."
        )
