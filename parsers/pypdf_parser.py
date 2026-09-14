"""PyPDF — pure-Python, local, text-layer only."""
from pypdf import PdfReader

NAME = "PyPDF"
KIND = "local"


def extract(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)
