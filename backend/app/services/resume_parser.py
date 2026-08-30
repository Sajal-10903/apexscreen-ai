"""Resume PDF parser using PyMuPDF (fitz)."""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str | Path) -> str:
    """Extract text from a PDF file using PyMuPDF.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If the file is not a valid PDF or is empty.
        FileNotFoundError: If the file does not exist.
    """
    import fitz  # PyMuPDF

    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.suffix.lower() == ".pdf":
        raise ValueError(f"Unsupported file type: {file_path.suffix}. Only PDF files are supported.")

    try:
        doc = fitz.open(str(file_path))
    except Exception as e:
        logger.error(f"Failed to open PDF: {e}")
        raise ValueError(f"Invalid or corrupted PDF file: {e}")

    page_count = doc.page_count
    if page_count == 0:
        doc.close()
        raise ValueError("PDF file contains no pages.")

    text_parts = []
    for page_num in range(page_count):
        page = doc[page_num]
        page_text = page.get_text("text")
        if page_text.strip():
            text_parts.append(page_text)

    doc.close()

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError("PDF file contains no extractable text (might be scanned/image-based).")

    # Basic cleaning
    full_text = _clean_text(full_text)

    logger.info(f"Extracted {len(full_text)} characters from {page_count} pages")
    return full_text


def parse_text_resume(text: str) -> str:
    """Process a plain-text resume.

    Args:
        text: Raw resume text.

    Returns:
        Cleaned text.

    Raises:
        ValueError: If text is empty.
    """
    if not text or not text.strip():
        raise ValueError("Resume text is empty.")

    return _clean_text(text)


def _clean_text(text: str) -> str:
    """Clean extracted text: normalize whitespace, remove control chars."""
    # Remove null bytes and control characters (keep newlines/tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()
