"""Compare chunk sizes and title weighting on the fixed retrieval evaluation set."""
import json
from app.core.config import CORPUS_PATH
from app.evaluation.questions import CASES
from app.services.retrieval import retrieve


def main():
    records = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    results = []
    for chunk_words, title_boost in ((120, 0.0), (120, 0.6), (250, 0.0), (250, 0.6), (500, 0.6)):
        misses = []
        for question, expected in CASES:
            top5 = [item["section"] for item in retrieve(
                question, records, top_k=5, chunk_words=chunk_words, title_boost=title_boost)]
            if expected not in top5:
                misses.append({"question": question, "expected": expected, "top5": top5})
        hits = len(CASES) - len(misses)
        results.append({"chunk_words": chunk_words, "title_boost": title_boost,
                        "hit_rate_at_5": hits / len(CASES), "hits": hits,
                        "total": len(CASES), "misses": misses})
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
