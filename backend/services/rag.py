"""Compose retrieval + Ollama generation into a single answer call."""
from typing import Dict, Any, List
import httpx

from .embeddings import embed_text
from .vector_store import query as vector_query

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

PROMPT_TEMPLATE = """Context:
{context}

Question:
{question}

Instructions:
Answer the question using only the provided context. If the answer is not in the context, say you do not know based on the uploaded documents.

Output:
Return only the answer."""


def answer_question(question: str, top_k: int = 4) -> Dict[str, Any]:
    q_embedding = embed_text(question)
    hits = vector_query(q_embedding, top_k=top_k)

    if not hits:
        return {
            "answer": "I do not know based on the uploaded documents. No documents have been indexed yet.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(h["text"] for h in hits)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    answer = _call_ollama(prompt)

    sources: List[Dict[str, Any]] = [
        {"source": h["source"], "snippet": _short(h["text"])} for h in hits
    ]
    return {"answer": answer, "sources": sources}


def _short(text: str, n: int = 300) -> str:
    text = text.strip().replace("\n", " ")
    return text if len(text) <= n else text[:n] + "..."


def _call_ollama(prompt: str) -> str:
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return (data.get("response") or "").strip()
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Could not reach Ollama at http://localhost:11434. "
            "Make sure Ollama is installed and running, and that you have run 'ollama run mistral'."
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(f"Ollama returned an error: {exc.response.status_code} {exc.response.text}") from exc
