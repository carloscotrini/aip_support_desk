# Issue 06 — KB-EMBED: Knowledge Base Embedding Pipeline

**Wave:** 2 (depends on: #01 KB-DOCS)
**Output:** `src/data/embeddings.py`, `src/data/kb_embeddings.npy`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the embedding strategy described in **Section 5: Agent Tools** (under `search_kb`).

## Dependencies

- **Issue #01 (KB-DOCS)** must be complete. Import knowledge base from:
  ```python
  from src.data.knowledge_base import KNOWLEDGE_BASE
  ```

## Task

Create a module that:
1. Computes sentence-transformer embeddings for all KB documents
2. Serializes them to a `.npy` file for fast loading
3. Provides a loader function for runtime use

## Requirements

### Embedding Computation (`compute_embeddings`)

- Use `sentence-transformers` library with a small, fast model (e.g., `all-MiniLM-L6-v2`)
- Split each KB document's `content` into chunks of ~200 words (simple split on paragraphs or sentences — no need for advanced chunking)
- Each chunk should carry metadata: `doc_id`, `title`, `chunk_index`
- Compute embeddings for all chunks
- Save to `src/data/kb_embeddings.npy` (embeddings array) and `src/data/kb_chunks.json` (chunk metadata + text)

### Loader Function (`load_embeddings`)

- Loads `.npy` and `.json` at runtime
- Returns a tuple: `(embeddings_array, chunks_list)` where `chunks_list` is a list of dicts with `doc_id`, `title`, `chunk_index`, `text`
- Must work without re-running the embedding model (load only, no compute)

### Script Entry Point

- Include an `if __name__ == "__main__"` block that runs `compute_embeddings()` and saves the output files
- Print progress: "Computing embeddings for {n} chunks..." / "Saved to ..."

## Output Format

```python
# src/data/embeddings.py

import numpy as np
import json

def compute_embeddings():
    """Compute and save embeddings for all KB documents."""
    ...

def load_embeddings():
    """Load pre-computed embeddings and chunk metadata."""
    ...
    return embeddings_array, chunks_list

if __name__ == "__main__":
    compute_embeddings()
```

## Acceptance Criteria

- [ ] Embeddings computed using `sentence-transformers` (not an API)
- [ ] Chunks carry `doc_id`, `title`, `chunk_index`, `text` metadata
- [ ] `.npy` and `.json` files are saved and loadable without the embedding model
- [ ] `load_embeddings()` returns `(np.ndarray, list[dict])`
- [ ] Module is importable: `from src.data.embeddings import load_embeddings`
