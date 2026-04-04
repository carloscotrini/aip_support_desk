# Issue 07 — TOOL-RAG: search_kb Tool

**Wave:** 3 (depends on: #06 KB-EMBED)
**Output:** `src/tools/search_kb.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the `search_kb` tool from **Section 5: Agent Tools**.

## Dependencies

- **Issue #06 (KB-EMBED)** must be complete. Import the loader:
  ```python
  from src.data.embeddings import load_embeddings
  ```

## Task

Implement the `search_kb(query)` tool that performs cosine similarity search over pre-computed KB embeddings.

## Requirements

### `search_kb(query, top_k=3) -> list[dict]`

1. **Encode the query** using the same `sentence-transformers` model (`all-MiniLM-L6-v2`)
2. **Compute cosine similarity** between the query embedding and all chunk embeddings using `sklearn.metrics.pairwise.cosine_similarity`
3. **Return top-k results** as a list of dicts:
   ```python
   [
       {
           "doc_id": "KB-001",
           "title": "Exporting Reports: Mileage, Fuel & Compliance",
           "chunk_index": 0,
           "text": "...",
           "similarity_score": 0.87
       },
       ...
   ]
   ```
4. **Print a business-legible trace** for each result:
   ```
   [TOOL: search_kb] Query: "monthly mileage report export"
   [TOOL: search_kb] Result 1: KB-001 "Exporting Reports..." (score: 0.87)
   [TOOL: search_kb] Result 2: KB-003 "Standard Customer Billing..." (score: 0.42)
   [TOOL: search_kb] Result 3: KB-004 "New Customer Onboarding..." (score: 0.38)
   ```

### Lazy Loading

- Embeddings and the sentence-transformer model should be loaded **once** on first call (module-level cache or singleton pattern), not on every invocation

### Tool Schema

Export a JSON-compatible schema for LLM function-calling:

```python
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
```

## Output Format

```python
# src/tools/search_kb.py

def search_kb(query: str, top_k: int = 3) -> list[dict]:
    ...

SEARCH_KB_SCHEMA = { ... }
```

## Acceptance Criteria

- [ ] Returns top-k chunks with `doc_id`, `title`, `text`, `similarity_score`
- [ ] Uses `sklearn.metrics.pairwise.cosine_similarity` (not a custom implementation)
- [ ] Prints business-legible trace on each call
- [ ] Embeddings loaded lazily (once, not per call)
- [ ] Tool schema exported
- [ ] Module is importable: `from src.tools.search_kb import search_kb, SEARCH_KB_SCHEMA`
