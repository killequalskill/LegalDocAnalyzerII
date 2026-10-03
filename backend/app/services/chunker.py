from typing import List, Optional
from app.models.documents import PageContent, DocumentChunkData
from app.services.chunking_utils import (
    detect_section_heading,
    detect_clause_id,
    estimate_tokens,
)


class DocumentChunker:
    """
    Hierarchical chunking strategy that respects document structure.

    Strategy:
    1. Process each page independently
    2. Detect sections/clauses using heuristics
    3. Group lines into logical chunks
    4. Keep chunks within token limits (300-2000)
    5. Preserve page numbers and section metadata
    """

    MIN_CHUNK_TOKENS = 50
    MAX_CHUNK_TOKENS = 2000
    TARGET_CHUNK_TOKENS = 800

    def chunk_documents(self, pages: List[PageContent]) -> List[DocumentChunkData]:
        """
        Convert list of pages into list of chunks with metadata.
        """
        chunks = []

        for page in pages:
            page_chunks = self._chunk_page(page)
            chunks.extend(page_chunks)

        return chunks

    def _chunk_page(self, page: PageContent) -> List[DocumentChunkData]:
        """
        Chunk a single page using hierarchical strategy.
        """
        lines = page.text.split("\n")
        chunks = []
        current_chunk = []
        current_section = None
        current_clause_id = None
        char_offset = 0

        for line in lines:
            stripped = line.strip()

            if not stripped:
                # Empty line—add to current chunk if we have content
                if current_chunk:
                    current_chunk.append("")
                continue

            # Check if this is a section heading
            if detect_section_heading(stripped):
                # Save current chunk if it has content
                if current_chunk:
                    chunk_text = "\n".join(current_chunk).strip()
                    if chunk_text:
                        chunks.append(
                            self._create_chunk(
                                chunk_text,
                                page.page_number,
                                current_section,
                                current_clause_id,
                                char_offset,
                            )
                        )
                    char_offset += len("\n".join(current_chunk))

                # Start new section
                current_section = stripped
                current_clause_id = detect_clause_id(stripped)
                current_chunk = [stripped]
                char_offset = 0

            else:
                # Regular content line
                current_chunk.append(stripped)

                # Check if chunk is getting too large
                chunk_tokens = estimate_tokens("\n".join(current_chunk))
                if chunk_tokens > self.TARGET_CHUNK_TOKENS:
                    # Try to split at paragraph boundary
                    if len(current_chunk) > 1:
                        # Keep last line for next chunk
                        next_chunk_first = current_chunk[-1]
                        chunk_text = "\n".join(current_chunk[:-1]).strip()

                        if chunk_text and estimate_tokens(chunk_text) >= self.MIN_CHUNK_TOKENS:
                            chunks.append(
                                self._create_chunk(
                                    chunk_text,
                                    page.page_number,
                                    current_section,
                                    current_clause_id,
                                    char_offset,
                                )
                            )
                            char_offset += len(chunk_text)
                            current_chunk = [next_chunk_first]

        # Save final chunk
        if current_chunk:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text and estimate_tokens(chunk_text) >= self.MIN_CHUNK_TOKENS:
                chunks.append(
                    self._create_chunk(
                        chunk_text,
                        page.page_number,
                        current_section,
                        current_clause_id,
                        char_offset,
                    )
                )

        return chunks

    def _create_chunk(
        self,
        text: str,
        page_number: int,
        section_name: Optional[str],
        clause_id: Optional[str],
        char_start: int,
    ) -> DocumentChunkData:
        """Create a DocumentChunkData object."""
        return DocumentChunkData(
            page_number=page_number,
            section_name=section_name,
            clause_id=clause_id,
            text=text,
            char_start=char_start,
            char_end=char_start + len(text),
        )
