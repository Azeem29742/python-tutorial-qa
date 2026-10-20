"""HTTP routes for question answering."""
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.corpus import load_records
from app.services.generation import ABSTENTION, generate_answer
from app.services.retrieval import retrieve

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/ask")
def ask(payload: QuestionRequest) -> dict[str, Any]:
    passages = retrieve(payload.question, load_records(), payload.top_k)
    if not passages or passages[0]["score"] < 0.2:
        return {"answer": ABSTENTION, "sources": []}
    return {
        "answer": generate_answer(payload.question, passages),
        "sources": [{key: item[key] for key in ("section", "url", "text", "score")} for item in passages],
    }
