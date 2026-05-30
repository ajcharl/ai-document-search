"""Persistent ChromaDB collection used for storing and retrieving chunks."""
import os
import uuid
from typing import List, Dict, Any

import chromadb

_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_data")
_COLLECTION_NAME = "documents"

_client: chromadb.api.ClientAPI | None = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        os.makedirs(_PERSIST_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=_PERSIST_DIR)
        # We pass embeddings manually, so disable Chroma's built-in embedder.
        _collection = _client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(chunks: List[str], embeddings: List[List[float]], source: str) -> int:
    if not chunks:
        return 0
    collection = _get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def query(embedding: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
    collection = _get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
    )
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    dists = (results.get("distances") or [[]])[0]
    out: List[Dict[str, Any]] = []
    for doc, meta, dist in zip(docs, metas, dists):
        out.append({"text": doc, "source": (meta or {}).get("source", "unknown"), "distance": dist})
    return out
