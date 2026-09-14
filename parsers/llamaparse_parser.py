"""LlamaParse — cloud, LLM-assisted, aimed at complex layouts and tables.

Requires LLAMA_CLOUD_API_KEY.
"""
import os

NAME = "LlamaParse"
KIND = "cloud"


def extract(pdf_path: str) -> str:
    import nest_asyncio
    from llama_parse import LlamaParse

    nest_asyncio.apply()

    api_key = os.environ["LLAMA_CLOUD_API_KEY"]
    parser = LlamaParse(api_key=api_key, result_type="text")  # or "markdown"

    documents = parser.load_data(pdf_path)
    return "\n".join(doc.text for doc in documents)
