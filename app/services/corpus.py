"""Read and validate the locally indexed tutorial corpus."""
import json
from typing import Any
from fastapi import HTTPException
from app.core.config import CORPUS_PATH


def load_records() -> list[dict[str, Any]]:
    if not CORPUS_PATH.exists():
        raise HTTPException(status_code=503, detail="Tutorial index missing. Run `uv run python scripts/ingest.py` first.")
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
