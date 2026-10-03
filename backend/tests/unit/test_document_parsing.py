import pytest
from pathlib import Path
import io
import PyPDF2


@pytest.fixture
def sample_pdf():
    """Create a minimal PDF for testing."""
    pdf_buffer = io.BytesIO()
    writer = PyPDF2.PdfWriter()

    # Create a simple 2-page PDF with text
    reader = PyPDF2.PdfReader(io.BytesIO(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/MediaBox[0 0 612 792]/Contents 5 0 R>>endobj 4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj 5 0 obj<</Length 44>>stream\nBT /F1 12 Tf 50 750 Td (Test Document) Tj ET\nendstream endobj xref 0 6 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n 0000000115 00000 n 0000000244 00000 n 0000000353 00000 n trailer<</Size 6/Root 1 0 R>>startxref 447 %%EOF"))

    # For simplicity, return a properly formatted PDF as bytes
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "AGREEMENT")
    c.drawString(100, 730, "")
    c.drawString(100, 700, "1. PAYMENT TERMS")
    c.drawString(100, 680, "Licensee shall pay Licensor $10,000 per annum.")
    c.drawString(100, 660, "")
    c.drawString(100, 630, "2. TERMINATION")
    c.drawString(100, 610, "Either party may terminate with 30 days written notice.")
    c.showPage()
    c.drawString(100, 750, "CONFIDENTIALITY")
    c.drawString(100, 730, "")
    c.drawString(100, 700, "3.1 Definition of Confidential Information")
    c.drawString(100, 680, "Confidential Information means all non-public data disclosed.")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
