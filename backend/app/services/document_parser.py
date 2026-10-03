import fitz
from typing import List, Tuple
from app.models.documents import PageContent


def extract_text_from_pdf(file_path: str) -> List[PageContent]:
    """
    Extract text from PDF using PyMuPDF (fitz).
    Returns list of PageContent objects, one per page.

    Each page preserves:
    - Page number (1-indexed)
    - Full text content
    - Metadata
    """
    pages = []

    try:
        pdf_doc = fitz.open(file_path)

        for page_num in range(len(pdf_doc)):
            page = pdf_doc[page_num]
            text = page.get_text()

            pages.append(
                PageContent(
                    page_number=page_num + 1,  # 1-indexed
                    text=text.strip(),
                    metadata={"page_count": len(pdf_doc)},
                )
            )

        pdf_doc.close()

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    return pages
