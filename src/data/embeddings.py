# src/data/embeddings.py
"""
Knowledge Base embedding pipeline for Meridian Fleet Solutions support desk.

Computes sentence-transformer embeddings for KB documents, splits content into
~200-word chunks with metadata, and serializes to .npy / .json for fast loading.
"""

import json
from pathlib import Path

import numpy as np

from src.data.knowledge_base import KNOWLEDGE_BASE

_DATA_DIR = Path(__file__).parent
_EMBEDDINGS_PATH = _DATA_DIR / "kb_embeddings.npy"
_CHUNKS_PATH = _DATA_DIR / "kb_chunks.json"

MODEL_NAME = "all-MiniLM-L6-v2"


def _split_into_chunks(text: str, target_words: int = 200) -> list[str]:
    """Split text into chunks of approximately *target_words* words.

    Strategy: split on double-newlines (paragraphs) first, then merge small
    paragraphs and split large ones to stay near the target size.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para.split())
        if current_len + para_len > target_words and current:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += para_len

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def compute_embeddings() -> None:
    """Compute and save embeddings for all KB documents."""
    from sentence_transformers import SentenceTransformer

    # Build chunks with metadata
    all_chunks: list[dict] = []
    for doc in KNOWLEDGE_BASE:
        text_chunks = _split_into_chunks(doc["content"])
        for idx, text in enumerate(text_chunks):
            all_chunks.append(
                {
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "chunk_index": idx,
                    "text": text,
                }
            )

    print(f"Computing embeddings for {len(all_chunks)} chunks...")

    model = SentenceTransformer(MODEL_NAME)
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=False)

    np.save(_EMBEDDINGS_PATH, embeddings)
    with open(_CHUNKS_PATH, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"Saved embeddings to {_EMBEDDINGS_PATH}")
    print(f"Saved chunk metadata to {_CHUNKS_PATH}")


def load_embeddings() -> tuple[np.ndarray, list[dict]]:
    """Load pre-computed embeddings and chunk metadata."""
    embeddings = np.load(_EMBEDDINGS_PATH)
    with open(_CHUNKS_PATH) as f:
        chunks = json.load(f)
    return embeddings, chunks


if __name__ == "__main__":
    compute_embeddings()
