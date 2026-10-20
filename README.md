# Python Tutorial QA

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Package manager: uv](https://img.shields.io/badge/package%20manager-uv-6F42C1)](https://docs.astral.sh/uv/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%203.5%20Flash--Lite-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev/gemini-api/docs/models)

A small retrieval-augmented question-answering API for the official [Python 3 Tutorial](https://docs.python.org/3/tutorial/). Ask a question and receive a concise answer with the tutorial passages and links used to support it. When the retrieved documentation does not answer the question, the service abstains instead of guessing.

## Features

- FastAPI endpoint for question answering, with interactive OpenAPI docs.
- Local lexical retrieval with configurable chunk size and section-title weighting.
- Gemini answer generation grounded in retrieved passages, with a clear abstention response.
- Source section, URL, passage text, and retrieval score included in each response.
- Repeatable 20-question Hit Rate@5 evaluation across five retrieval configurations.
- Tutorial content downloaded from the official documentation during ingestion; no API key is needed to ingest or evaluate.

## Quick start

### Requirements

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) for generated answers (optional for retrieval-only mode)

### Install and configure

```powershell
uv sync
Copy-Item .env.example .env
```

Open `.env` and set `GEMINI_API_KEY` to your key. Keep this file private; it is excluded from Git. You can change the model with `GEMINI_MODEL`.

### Download the tutorial and run the evaluation

```powershell
uv run python scripts/ingest.py
uv run python scripts/evaluate.py
```

Ingestion reads the official tutorial index and saves the extracted sections to `data/tutorial.json`. This file is generated locally and ignored by Git. The evaluation uses the saved corpus and prints the results for all tested configurations.

### Start the API

```powershell
uv run uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and try `POST /ask`.

## API

### `POST /ask`

Request:

```json
{
  "question": "What is a list comprehension?",
  "top_k": 5
}
```

`question` must contain 3–1,000 characters. `top_k` is optional and can be from 1 to 10 (default: 5).

Response shape:

```json
{
  "answer": "A list comprehension is a concise way to create a list. [List Comprehensions]",
  "sources": [
    {
      "section": "List Comprehensions",
      "url": "https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions",
      "text": "List comprehensions provide a concise way to create lists...",
      "score": 1.6
    }
  ]
}
```

The example is illustrative. The exact answer, passage, score, and number of sources depend on the question and local corpus. If no relevant passage is found, the API returns an abstention with an empty `sources` list. If `GEMINI_API_KEY` is not configured, it returns the retrieved sources and a setup message instead of calling Gemini.

### `GET /health`

Returns `{"status":"ok"}` when the service is running.

## Design

The ingestion script follows chapter links from the Python Tutorial index, extracts subsection text and anchors, and stores records in JSON. At query time, the retriever splits each section into word-based chunks, tokenizes the question and passages, and ranks by lexical overlap with an additional section-title boost. Results are deduplicated by section before the top passages are sent to Gemini.

The generation prompt restricts answers to the retrieved text, requests a section citation, and defines an abstention response. The API also returns the passages themselves so users can inspect the evidence behind each answer. Retrieval is deterministic; generation requires a Gemini API key.

### Project structure

```text
app/
├── api/          # FastAPI routes and request schema
├── core/         # Shared configuration and text processing
├── evaluation/   # Fixed questions and benchmark runner
├── ingestion/    # Official tutorial downloader and parser
├── services/     # Corpus loading, retrieval, and Gemini generation
└── main.py       # FastAPI application
scripts/          # Ingestion and evaluation entry points
data/
├── evaluation_results.json  # Recorded benchmark results
└── tutorial.json            # Generated locally; not committed
```

## Retrieval evaluation

The benchmark contains 20 questions, each mapped to its expected tutorial subsection. A question counts as a hit when that subsection appears among the five highest-ranked distinct sections. The corpus snapshot used for the recorded results contained 132 sections across 16 tutorial pages, fetched on 20 October 2026.

| Chunk size | Title boost | Hits | Hit Rate@5 |
| ---: | ---: | ---: | ---: |
| 120 words | 0.0 | 16/20 | 80% |
| **120 words** | **0.6** | **17/20** | **85%** |
| 250 words | 0.0 | 15/20 | 75% |
| 250 words | 0.6 | 17/20 | 85% |
| 500 words | 0.6 | 17/20 | 85% |

Adding title weighting at 120 words improved Hit Rate@5 by 5 percentage points. At zero title boost, increasing chunk size from 120 to 250 words reduced it by 5 points. The selected API defaults are 120-word chunks and a 0.6 title boost. Full per-question results are in [`data/evaluation_results.json`](data/evaluation_results.json).

### Three observed retrieval misses

These questions missed their expected section with the selected configuration:

1. **“What does the with statement do when opening a file?”** The expected section is `Predefined Clean-up Actions`. Other file-related passages ranked higher because the lexical scorer overweights shared words such as “file.”
2. **“How do I import a module?”** The expected section is `Modules`. Related sections about package imports and the module search path ranked higher; the current scorer does not resolve the broad intent of “import.”
3. **“Which module provides filesystem operations such as listing a directory?”** The expected section is `Operating system interface`. Literal overlap with “list” favored list-related passages and did not connect “filesystem operations” with the `os` module.

## Limitations and next steps

The retriever is lexical, so it can miss paraphrases and related concepts. The benchmark is small and measures section retrieval, not answer faithfulness or latency. Next steps are to compare BM25 and embedding-based retrieval, add questions whose answers are absent to evaluate abstention, and assess generated-answer faithfulness separately.

## Configuration and security

Copy `.env.example` to `.env`, add your `GEMINI_API_KEY`, and optionally set `GEMINI_MODEL`. The default model is `gemini-3.5-flash-lite`; see Google's [model documentation](https://ai.google.dev/gemini-api/docs/models) for current model availability. Never commit or share `.env` or your API key. The tutorial corpus is downloaded from [docs.python.org](https://docs.python.org/3/tutorial/) and is not committed.

