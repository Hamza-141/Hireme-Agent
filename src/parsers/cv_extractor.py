"""CV text extraction from uploaded files."""

import os
import tempfile

import fitz  # PyMuPDF
from docx import Document


def extract_text(uploaded_file) -> str:
    """Extract all readable text from a Streamlit UploadedFile.

    Supports PDF (.pdf) and Word (.docx) formats.
    The file is written to a temporary location on disk, processed,
    and the temp file is removed afterwards — even if an error occurs.

    Args:
        uploaded_file: A Streamlit ``UploadedFile`` object.

    Returns:
        The full extracted text as a single string.

    Raises:
        ValueError: If the file type is not PDF or DOCX.
    """
    filename = uploaded_file.name
    extension = os.path.splitext(filename)[1].lower()

    if extension not in (".pdf", ".docx"):
        raise ValueError(
            f"Unsupported file type '{extension}'. "
            "Please upload a PDF (.pdf) or Word (.docx) file."
        )

    # Write uploaded bytes to a temp file so libraries can read from disk.
    tmp_path = None
    try:
        suffix = extension  # e.g. ".pdf" or ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        if extension == ".pdf":
            text = _extract_pdf(tmp_path)
        else:
            text = _extract_docx(tmp_path)

    finally:
        # Always clean up the temp file.
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

    print(f"[cv_extractor] Extracted {len(text)} characters from '{filename}'")
    return text


# ── Private helpers ──────────────────────────────────────────────────────────


def _extract_pdf(path: str) -> str:
    """Return all text from a PDF file using PyMuPDF."""
    doc = fitz.open(path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages).strip()


def _extract_docx(path: str) -> str:
    """Return all text from a DOCX file using python-docx."""
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs).strip()
