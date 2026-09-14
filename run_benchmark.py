"""Run every available parser over the same PDFs and record what each produced.

Local parsers always run. Cloud parsers run only when their credentials are
present, so the harness is useful without an AWS or LlamaCloud account.

    python run_benchmark.py --input samples/ --out results/
"""
import argparse
import importlib
import json
import time
from pathlib import Path

from dotenv import load_dotenv

PARSERS = [
    ("parsers.pypdf_parser", []),
    ("parsers.pdfminer_parser", []),
    ("parsers.pdfplumber_parser", []),
    ("parsers.llamaparse_parser", ["LLAMA_CLOUD_API_KEY"]),
    ("parsers.textract_parser", ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]),
]


def available(required_env):
    import os
    return [k for k in required_env if not os.getenv(k)]


def run_one(module, pdf_path):
    """Return (text, seconds) or (None, error) — never raise, so one broken
    parser does not abandon the whole run."""
    start = time.perf_counter()
    try:
        text = module.extract(str(pdf_path))
        return text, time.perf_counter() - start, None
    except Exception as exc:  # noqa: BLE001 - reporting, not handling
        return None, time.perf_counter() - start, f"{type(exc).__name__}: {exc}"


def main():
    load_dotenv()

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="samples", help="directory of PDFs")
    ap.add_argument("--out", default="results", help="where to write extractions")
    args = ap.parse_args()

    pdfs = sorted(Path(args.input).glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {args.input}/")

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    summary = []

    for pdf in pdfs:
        print(f"\n{pdf.name}")
        print("-" * len(pdf.name))

        for module_path, required_env in PARSERS:
            module = importlib.import_module(module_path)
            missing = available(required_env)

            if missing:
                print(f"  {module.NAME:<14} skipped (set {', '.join(missing)})")
                continue

            text, seconds, error = run_one(module, pdf)

            if error:
                print(f"  {module.NAME:<14} FAILED  {error}")
                summary.append({
                    "document": pdf.name, "parser": module.NAME, "kind": module.KIND,
                    "seconds": round(seconds, 2), "characters": None, "error": error,
                })
                continue

            destination = out_root / pdf.stem
            destination.mkdir(parents=True, exist_ok=True)
            (destination / f"{module.NAME}.txt").write_text(text, encoding="utf-8")

            print(f"  {module.NAME:<14} {seconds:6.2f}s  {len(text):>8,} chars")
            summary.append({
                "document": pdf.name, "parser": module.NAME, "kind": module.KIND,
                "seconds": round(seconds, 2), "characters": len(text), "error": None,
            })

    (out_root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"\nExtractions written to {out_root}/<document>/<parser>.txt")
    print(f"Timings written to {out_root}/summary.json")
    print(
        "\nCharacter count and wall-clock time are mechanical measures. They tell "
        "you nothing about reading order or whether a table survived - open the "
        "files side by side and judge that yourself."
    )


if __name__ == "__main__":
    main()
