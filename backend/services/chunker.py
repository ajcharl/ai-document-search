"""Split long text into overlapping word-based chunks."""
from typing import List


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    # Normalize whitespace, then split on words for simple, predictable chunks.
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(words), step):
        window = words[start:start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks
