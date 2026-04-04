# src/tools/search_kb.py
"""
search_kb tool — cosine similarity search over pre-computed KB embeddings.
"""

from sklearn.metrics.pairwise import cosine_similarity

from src.data.embeddings import MODEL_NAME, load_embeddings

# Lazy-loaded module-level cache
_model = None
_embeddings = None
_chunks = None


def _ensure_loaded():
    """Load embeddings and model once on first call."""
    global _model, _embeddings, _chunks
    if _embeddings is None:
        _embeddings, _chunks = load_embeddings()
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)


def search_kb(query: str, top_k: int = 3) -> list[dict]:
    """Search the knowledge base for relevant support documentation.

    Returns top-k matching document chunks with similarity scores.
    """
    _ensure_loaded()

    query_embedding = _model.encode([query])
    similarities = cosine_similarity(query_embedding, _embeddings)[0]

    top_indices = similarities.argsort()[::-1][:top_k]

    results = []
    print(f'[TOOL: search_kb] Query: "{query}"')
    for rank, idx in enumerate(top_indices, 1):
        chunk = _chunks[idx]
        score = float(similarities[idx])
        result = {
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
            "similarity_score": round(score, 2),
        }
        results.append(result)
        title_short = chunk["title"][:30] + "..." if len(chunk["title"]) > 30 else chunk["title"]
        print(f'[TOOL: search_kb] Result {rank}: {chunk["doc_id"]} "{title_short}" (score: {score:.2f})')

    return results


SEARCH_KB_SCHEMA = {
    "name": "search_kb",
    "description": "Search the knowledge base for relevant support documentation. Returns top-k matching document chunks with similarity scores.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Natural language search query"}
        },
        "required": ["query"]
    }
}
