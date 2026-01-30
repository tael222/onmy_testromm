"""PDF handler module for ReadAlongBuddy - PDF upload and page extraction."""

import io
from PIL import Image

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def is_pdf_supported() -> bool:
    """Check if PyMuPDF is available."""
    return HAS_PYMUPDF


def extract_pages_from_pdf(pdf_bytes: bytes, dpi: int = 200) -> list[Image.Image]:
    """Extract all pages from a PDF as PIL Images.

    Args:
        pdf_bytes: Raw PDF file bytes
        dpi: Resolution for rendering pages
    Returns:
        List of PIL Images, one per page
    """
    if not HAS_PYMUPDF:
        raise RuntimeError("PyMuPDF가 설치되지 않았습니다. pip install PyMuPDF를 실행해 주세요.")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        images.append(img)

    doc.close()
    return images


def get_page_count(pdf_bytes: bytes) -> int:
    """Get number of pages in a PDF."""
    if not HAS_PYMUPDF:
        return 0
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = len(doc)
    doc.close()
    return count
