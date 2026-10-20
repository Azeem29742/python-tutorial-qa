"""Optional Gemini answer generation grounded only in retrieved passages."""
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

ABSTENTION = "The Python Tutorial does not provide this information."
MODEL_DEFAULT = "gemini-3.8-flash"


def generate_answer(question: str, passages: list[dict[str, Any]]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "LLM generation is not configured. Add GEMINI_API_KEY to your local .env file; retrieved sources are provided below."

    from google import genai

    context = "\n\n".join(f"[{p['section']}] {p['text']}" for p in passages)
    prompt = (
        "You answer questions only from the Python Tutorial passages below. "
        f"If the passages do not contain the answer, respond exactly: {ABSTENTION} "
        "Do not use outside knowledge. Cite the relevant section name.\n\n"
        f"Question: {question}\n\nTutorial passages:\n{context}"
    )
    client = genai.Client(api_key=api_key)
    response = client.interactions.create(
        model=os.getenv("GEMINI_MODEL", MODEL_DEFAULT),
        input=prompt,
    )
    return response.output_text or ABSTENTION
