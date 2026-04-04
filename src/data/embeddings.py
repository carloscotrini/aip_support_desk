# src/data/embeddings.py
"""
Knowledge Base embedding pipeline.

Computes sentence-transformer embeddings for all KB documents,
serializes them for fast loading, and provides a loader function.
"""

import json
import os
import numpy as np

# Paths for serialized embeddings
_DIR = os.path.dirname(os.path.abspath(__file__))
_EMBEDDINGS_PATH = os.path.join(_DIR, "kb_embeddings.npy")
_CHUNKS_PATH = os.path.join(_DIR, "kb_chunks.json")


def _chunk_text(text: str, max_words: int = 200) -> list[str]:
    """Split text into chunks of approximately max_words words on paragraph boundaries."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk: list[str] = []
    current_word_count = 0

    for para in paragraphs:
        para_words = len(para.split())
        if current_word_count + para_words > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_word_count = para_words
        else:
            current_chunk.append(para)
            current_word_count += para_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def compute_embeddings():
    """Compute and save embeddings for all KB documents."""
    from sentence_transformers import SentenceTransformer
    from src.data.knowledge_base import KNOWLEDGE_BASE

    model = SentenceTransformer("all-MiniLM-L6-v2")

    chunks_list = []
    for doc in KNOWLEDGE_BASE:
        text_chunks = _chunk_text(doc["content"])
        for i, chunk_text in enumerate(text_chunks):
            chunks_list.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "chunk_index": i,
                "text": chunk_text,
            })

    print(f"Computing embeddings for {len(chunks_list)} chunks...")
    texts = [c["text"] for c in chunks_list]
    embeddings = model.encode(texts, show_progress_bar=False)

    np.save(_EMBEDDINGS_PATH, embeddings)
    with open(_CHUNKS_PATH, "w") as f:
        json.dump(chunks_list, f, indent=2)

    print(f"Saved to {_EMBEDDINGS_PATH} and {_CHUNKS_PATH}")


def load_embeddings() -> tuple[np.ndarray, list[dict]]:
    """Load pre-computed embeddings and chunk metadata."""
    embeddings = np.load(_EMBEDDINGS_PATH)
    with open(_CHUNKS_PATH) as f:
        chunks_list = json.load(f)
    return embeddings, chunks_list


if __name__ == "__main__":
    compute_embeddings()
