"""AWS Textract — cloud OCR. Renders each page to an image first, so it is the
only option here that handles scanned documents.

Requires AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY and AWS_REGION.
"""
import io
import os

NAME = "AWS Textract"
KIND = "cloud"


def extract(pdf_path: str) -> str:
    import boto3
    import fitz  # PyMuPDF

    session = boto3.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
    client = session.client("textract", region_name=os.getenv("AWS_REGION", "us-east-1"))

    document = fitz.open(pdf_path)
    pages = []

    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        image_bytes = page.get_pixmap().tobytes()

        with io.BytesIO(image_bytes) as buffer:
            response = client.detect_document_text(Document={"Bytes": buffer.read()})

        # LINE blocks preserve reading order better than WORD blocks.
        lines = [b["Text"] for b in response["Blocks"] if b["BlockType"] == "LINE"]
        pages.append("\n".join(lines))

    return "\n\n".join(pages)
