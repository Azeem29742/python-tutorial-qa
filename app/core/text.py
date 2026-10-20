"""Normalize query and document terms for the lightweight lexical retriever."""
import re

STOPWORDS = {"a", "an", "and", "are", "as", "at", "be", "can", "do", "does", "for", "how", "i", "if", "in", "is", "it", "me", "of", "on", "or", "such", "that", "the", "this", "to", "what", "when", "which", "with"}


def normalize(token: str) -> str:
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        stem = token[:-3]
        return stem + "e" if stem.endswith("s") else stem
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("es") and not token.endswith("ses"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    return [term for word in re.findall(r"[a-z_][a-z0-9_]*", text.lower())
            if (term := normalize(word)) not in STOPWORDS]
