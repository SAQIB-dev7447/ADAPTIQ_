# services/ingestion.py
# Content extraction layer — called BEFORE any Supabase write, BEFORE any AI call.
# Rule: extract_text() raises ValueError on failure → caller returns 400 to frontend.

import fitz                     # PyMuPDF
import trafilatura
from docx import Document
import io

MAX_CHARS = 3000  # Hard cap — never send more than this to any AI call


def extract_text(source_type: str, content) -> str:
    """
    Extracts raw text from any input type.
    Returns plain string, truncated to MAX_CHARS.
    Raises ValueError if extraction fails.
    """
    if source_type == "paste":
        return _clean(str(content))

    elif source_type == "pdf":
        # content = bytes of the PDF file
        try:
            doc = fitz.open(stream=content, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Could not open PDF: {e}")
        text = ""
        for page in doc:
            text += page.get_text()
            if len(text) >= MAX_CHARS:
                break
        if not text.strip():
            raise ValueError("PDF appears to be empty or unreadable")
        return _clean(text)

    elif source_type == "url":
        # content = URL string
        downloaded = trafilatura.fetch_url(content)
        if not downloaded:
            raise ValueError("Could not fetch URL content")
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            output_format="txt"
        )
        if not text:
            raise ValueError("No readable content found at URL")
        return _clean(text)

    elif source_type == "docx":
        # content = bytes of the DOCX file
        try:
            doc = Document(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"Could not open DOCX: {e}")
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        if not text.strip():
            raise ValueError("DOCX appears to be empty")
        return _clean(text)

    else:
        raise ValueError(f"Unknown source type: {source_type}")


def _clean(text: str) -> str:
    """Strips excess whitespace and enforces the character cap."""
    text = " ".join(text.split())
    return text[:MAX_CHARS]
