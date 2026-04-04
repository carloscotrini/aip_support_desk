# Issue 16 — SETUP: Notebook Setup Cell

**Wave:** 7 (depends on: #06 KB-EMBED)
**Output:** `src/cells/setup.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 7, Row 1: SETUP** — the first cell participants run.

## Dependencies

- **Issue #06 (KB-EMBED)**: `from src.data.embeddings import load_embeddings`
- All other modules should be importable by the time this runs, but this cell only directly uses the embedding loader and config.

## Task

Create a module that provides the setup/initialization logic for the Colab notebook — dependency installation, API key configuration, embedding loading, and the `DEMO_MODE` toggle.

## Requirements

### `install_dependencies() -> None`

Prints and runs pip install commands. In Colab these run as `!pip install`:

```python
DEPENDENCIES = [
    "anthropic",
    "sentence-transformers",
    "scikit-learn",
]
```

Since this will be called from a notebook cell, provide the install command strings. The actual `!pip install` will be in the notebook cell itself — this function just prints what's needed and verifies imports.

### `configure_api_key() -> str | None`

- If `DEMO_MODE` is True, print a message and return None
- If `DEMO_MODE` is False, use `getpass.getpass()` to prompt for an API key
- Return the key (or None in demo mode)
- Print status:
  ```
  [SETUP] DEMO_MODE=True — using pre-scripted responses (no API key needed)
  ```
  or:
  ```
  [SETUP] Live mode — enter your Anthropic API key:
  ```

### `initialize() -> dict`

The main setup function that returns a config dict:

```python
def initialize(demo_mode: bool = True) -> dict:
    """
    Run all setup steps and return a config dict.

    Returns:
        {
            "demo_mode": bool,
            "api_key": str | None,
            "embeddings_loaded": bool,
            "tools_available": list[str],
        }
    """
```

1. Set `DEMO_MODE` flag
2. Configure API key (if live mode)
3. Load embeddings via `load_embeddings()`
4. Import and verify all tool modules are available
5. Print a summary box:

```
╔══════════════════════════════════════════════════════════╗
║  ✅ SETUP COMPLETE                                      ║
╠══════════════════════════════════════════════════════════╣
║  Mode:        DEMO (pre-scripted responses)              ║
║  Embeddings:  Loaded (23 chunks from 5 KB documents)     ║
║  Tools:       5 available                                ║
║    • search_kb                                           ║
║    • query_customer_db                                   ║
║    • send_email                                          ║
║    • escalate                                            ║
║    • request_info                                        ║
╠══════════════════════════════════════════════════════════╣
║  Ready! Change ACTIVE_TICKET and run the cells below.    ║
╚══════════════════════════════════════════════════════════╝
```

### Module-level Config

```python
DEMO_MODE = True  # Default: pre-scripted responses, no API key needed

DEPENDENCIES = [
    "anthropic",
    "sentence-transformers",
    "scikit-learn",
]
```

## Output Format

```python
# src/cells/setup.py

DEMO_MODE = True
DEPENDENCIES = ["anthropic", "sentence-transformers", "scikit-learn"]

def install_dependencies() -> None:
    ...

def configure_api_key(demo_mode: bool = True) -> str | None:
    ...

def initialize(demo_mode: bool = True) -> dict:
    ...
```

## Acceptance Criteria

- [ ] `initialize()` returns a config dict with mode, API key, embedding status, tool list
- [ ] Demo mode works without any API key
- [ ] Live mode prompts for API key via `getpass`
- [ ] Prints a clear summary box showing what's ready
- [ ] Embedding loading is verified (reports chunk count)
- [ ] All 5 tools verified as importable
- [ ] Module is importable: `from src.cells.setup import initialize, DEMO_MODE`
