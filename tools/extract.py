"""
Text extraction, quality gating, and OCR-artifact cleanup.

Two failures this guards against, both of which corrupted the library before:

1. Image-only PDFs extract almost nothing. Ingested silently, they become empty
   records that are retrievable but useless — present in the index, contributing
   nothing. These are quarantined instead.

2. OCR'd text carries soft hyphens and mid-word line breaks ("work-\\nable" ->
   "work­able"). Chunking that text embeds broken words, which no chunker fixes
   because the damage is upstream.
"""

import re
import os

# A real page of prose yields well over this. Scans yield near zero.
MIN_CHARS_PER_PAGE = 100


def clean_text(text: str) -> str:
    """Repair OCR artifacts that would otherwise be embedded verbatim."""
    if not text:
        return ""

    # Soft hyphen (U+00AD) and its OCR lookalikes, used for line-break
    # hyphenation. "spirit­ual" -> "spiritual".
    text = text.replace("­", "")

    # Hyphen + newline mid-word: "work-\nable" -> "workable". Requires a
    # lowercase letter on both sides so real compounds survive.
    text = re.sub(r"([a-z])-\s*\n\s*([a-z])", r"\1\2", text)

    # Single newlines inside a paragraph become spaces; blank lines (paragraph
    # breaks) are preserved so RecursiveChunker can still see structure.
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse runs of whitespace, and limit blank lines to a paragraph break.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Page-number lines left behind by extraction.
    text = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", text)

    return text.strip()


def extract_pdf(path: str):
    """Return (text, page_count). Never raises."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(path)
        pages = reader.pages
        parts = []
        for page in pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                parts.append("")
        return "\n".join(parts), len(pages)
    except Exception:
        return "", 0


def extract_docx(path: str):
    try:
        import docx
        d = docx.Document(path)
        text = "\n".join(p.text for p in d.paragraphs)
        return text, max(1, len(text) // 2000)
    except Exception:
        return "", 0


def extract(path: str):
    """
    Extract and clean a document.

    Returns a dict with: text, pages, chars, ok, reason.
    `ok` is False when the document should be quarantined rather than ingested.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        raw, pages = extract_pdf(path)
    elif ext in (".docx", ".doc"):
        raw, pages = extract_docx(path)
    elif ext in (".txt", ".md"):
        try:
            raw = open(path, encoding="utf-8", errors="ignore").read()
            pages = max(1, len(raw) // 2000)
        except OSError:
            raw, pages = "", 0
    else:
        return {"text": "", "pages": 0, "chars": 0, "ok": False,
                "reason": f"unsupported type {ext}"}

    text = clean_text(raw)
    chars = len(text)

    if chars == 0:
        return {"text": "", "pages": pages, "chars": 0, "ok": False,
                "reason": "no text extracted — likely an image-only scan; needs OCR"}

    if pages and chars / pages < MIN_CHARS_PER_PAGE:
        return {"text": text, "pages": pages, "chars": chars, "ok": False,
                "reason": f"only {chars // pages} chars/page — likely a scan; needs OCR"}

    return {"text": text, "pages": pages, "chars": chars, "ok": True,
            "reason": ""}
