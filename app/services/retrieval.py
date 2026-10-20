"""Chunked lexical retrieval shared by the API and benchmark."""
from typing import Any
from app.core.text import tokenize


def iter_chunks(records: list[dict[str, Any]], chunk_words: int):
    for record in records:
        words = record["text"].split()
        for start in range(0, len(words), chunk_words):
            yield {**record, "text": " ".join(words[start:start + chunk_words])}


def retrieve(question: str, records: list[dict[str, Any]], top_k: int = 5,
             chunk_words: int = 120, title_boost: float = 0.6) -> list[dict[str, Any]]:
    terms = set(tokenize(question))
    ranked = []
    for passage in iter_chunks(records, chunk_words):
        body = set(tokenize(passage["text"]))
        title = set(tokenize(passage["section"]))
        score = len(terms & body) / max(1, len(terms)) + title_boost * len(terms & title)
        if score:
            ranked.append((score, passage))
    ranked.sort(key=lambda row: (-row[0], row[1]["section"]))
    results = []
    seen = set()
    for score, passage in ranked:
        if passage["section"] in seen:
            continue
        results.append({**passage, "score": round(score, 4)})
        seen.add(passage["section"])
        if len(results) == top_k:
            break
    return results

