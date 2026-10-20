"""Application settings and filesystem locations."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CORPUS_PATH = DATA_DIR / "tutorial.json"
DOCS_INDEX_URL = "https://docs.python.org/3/tutorial/index.html"
