# 📑 PDF Parser Benchmark

**Five PDF parsers, one harness, the same document — so the choice is measured instead of inherited.**

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LlamaParse](https://img.shields.io/badge/LlamaParse-6E56CF?style=flat-square)](https://cloud.llamaindex.ai)
[![AWS Textract](https://img.shields.io/badge/AWS_Textract-232F3E?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/textract/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

---

## Why this exists

Every document-AI pipeline opens with the same decision, and almost nobody makes it deliberately: **which parser?** The usual answer is whichever one appeared in the first tutorial the team read.

It matters more than it looks. A parser that scrambles a two-column layout or flattens a table into word soup doesn't fail loudly — it fails *silently*, and the RAG system built on top of it starts retrieving nonsense three weeks later with no obvious cause. By the time anyone investigates the answer quality, nobody thinks to look at page one.

So: run them all against the same document, keep every output, and look at them side by side.

## What it does

```bash
python run_benchmark.py --input samples/ --out results/
```

```
testing.pdf
-----------
  PyPDF            0.31s     18,442 chars
  PDFMiner         1.12s     18,901 chars
  PDFPlumber       2.04s     18,887 chars
  LlamaParse      11.60s     19,233 chars
  AWS Textract    14.28s     19,010 chars
```

Every extraction is written to `results/<document>/<parser>.txt` so you can diff them directly, plus a `summary.json` with timings and character counts.

> **On the numbers above:** they are illustrative of the output shape, not results I am reporting. Character count and wall-clock time are *mechanical* measures — they tell you how much text came out and how long it took, and nothing about whether the reading order survived or the table is still a table. That judgement needs your eyes on your documents, which is exactly what the side-by-side files are for.

**Cloud parsers are skipped automatically when their credentials aren't set**, so the harness is useful with no AWS or LlamaCloud account at all — you just get the three local ones.

---

## The five

| Parser | Where it runs | Handles scans? | Cost | Built for |
|---|---|---|---|---|
| **[PyPDF](https://pypdf.readthedocs.io)** | Local | ❌ text layer only | Free | Speed. Clean, text-native PDFs. |
| **[PDFMiner.six](https://pdfminersix.readthedocs.io)** | Local | ❌ text layer only | Free | Layout analysis — the engine several other tools build on. |
| **[PDFPlumber](https://github.com/jsvine/pdfplumber)** | Local | ❌ text layer only | Free | Tables and precise per-character positioning. |
| **[LlamaParse](https://cloud.llamaindex.ai)** | Cloud | ✅ | Per page, free tier | LLM-assisted parsing of complex layouts; markdown output aimed at RAG. |
| **[AWS Textract](https://aws.amazon.com/textract/)** | Cloud | ✅ OCR | Per page | Scanned documents, forms, key-value extraction at volume. |

### The first fork in the road

**Does your document have a text layer?**

If it's a scan or a photo, three of the five are immediately out — PyPDF, PDFMiner and PDFPlumber read the embedded text layer, and a scan doesn't have one. They won't error; they'll return empty strings or garbage, which is worse. You need OCR: Textract, or LlamaParse.

If it *does* have a text layer, start local. They're free, fast, and private, and on clean single-column documents the cloud parsers have very little to add.

### The second fork

**Can the document leave your infrastructure?**

LlamaParse and Textract mean shipping the document to a third party. For medical records, contracts, or anything under a data-residency obligation, that ends the discussion regardless of accuracy — local only.

---

## Method

The harness holds the variables still: same document, same machine, one adapter per parser behind an identical `extract(path) -> str` interface. What it deliberately does *not* do is score accuracy automatically.

**That's a choice, not an omission.** "Accuracy" for text extraction means reading order, table structure, header/footer handling and hyphenation — and a naive string-similarity score against ground truth rewards the wrong things. A parser that dumps every word in the wrong order can score well on character overlap while being useless downstream.

So the harness produces the artifacts, and the judgement stays human:

1. Run it on documents that are hard *in the way yours are hard* — multi-column, dense tables, scans, forms
2. Open `results/<document>/*.txt` side by side
3. Ask: did the reading order survive? Is the table still a table? Where did each one break?

**Record what you find in this README.** A results table for one person's document set is not a universal benchmark — it's a record of a decision, which is the useful thing.

### Limits, stated up front

- One sample document ships with the repo. Directional at best; add your own.
- No automated scoring, for the reason above.
- Wall-clock timings include network round-trips for cloud parsers, so they're not comparable to the local ones as pure processing cost.
- Parser versions are pinned in `requirements.txt` — results will shift as these tools change, which is itself a reason to re-run rather than trust a table from 2024.

---

## Run it

```bash
git clone https://github.com/MohanVishe/pdf-parser-benchmark.git
cd pdf-parser-benchmark

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Local parsers work immediately. For the cloud two:

```bash
cp .env.example .env
# LLAMA_CLOUD_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```

```bash
python run_benchmark.py --input samples/ --out results/
```

Drop your own PDFs into `samples/` — anything in there gets picked up.

---

## Layout

```
├── run_benchmark.py        # runs every available parser, writes outputs + timings
├── parsers/
│   ├── pypdf_parser.py
│   ├── pdfminer_parser.py
│   ├── pdfplumber_parser.py
│   ├── llamaparse_parser.py    # skipped without LLAMA_CLOUD_API_KEY
│   └── textract_parser.py      # skipped without AWS credentials
├── samples/                # test documents
└── results/                # extractions + summary.json (gitignored)
```

Every parser is one file exposing `extract(pdf_path) -> str`. Adding a sixth — Docling, Unstructured, Marker — means writing that function and adding one line to `PARSERS` in `run_benchmark.py`.

---

## What I'd add next

- **More documents, more domains.** One sample is a demo, not a benchmark.
- **Docling and Unstructured.io** — both have moved fast since this was written.
- **Structure-aware scoring**, so re-runs can be compared automatically without the naive-string-similarity trap. Probably table-cell F1 plus a reading-order metric rather than raw overlap.
- **End-to-end measurement**: same RAG pipeline, five different parsers, compare *answer* quality. Parser accuracy is a proxy — retrieval quality downstream is what actually pays.

## License

MIT — see [LICENSE](LICENSE).
