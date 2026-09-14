"""PDFPlumber — local, layout-aware, understands table structure."""
import pdfplumber

NAME = "PDFPlumber"
KIND = "local"


def extract(pdf_path: str) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
