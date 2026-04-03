# Issue 13 — CONTRAST: Frustrated Chatbot & RAG Isolation Cells

**Wave:** 6 (depends on: #07 TOOL-RAG, #03 TICKETS)
**Output:** `src/cells/contrast.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 7, Rows 5–6**: "The Frustrated Chatbot" and "RAG in Isolation".

## Dependencies

- **Issue #07 (TOOL-RAG)**: `from src.tools.search_kb import search_kb`
- **Issue #03 (TICKETS)**: `from src.data.tickets import TICKETS`

Ensure `src/cells/__init__.py` exists (create it if needed).

## Task

Create two functions that produce the "contrast" outputs used to set up the aha moment before the full agent loop is shown.

## Requirements

### 1. `run_frustrated_chatbot(ticket, llm_client=None, demo_response=None) -> str`

Simulates what a **plain chatbot** (no tools, no loop) would respond to the ticket.

- If `demo_response` is provided (a string), use it directly (for DEMO_MODE)
- If `llm_client` is provided, call the LLM with:
  - A simple system prompt: "You are a customer support agent for Meridian Fleet Solutions. Answer the customer's question."
  - The ticket body as the user message
  - **No tools**, **no loop** — just a single LLM call
- Print the response in a styled box:

```
╔══════════════════════════════════════════════════════════╗
║  🤖 CHATBOT RESPONSE (no tools, no reasoning loop)     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  "Thank you for reaching out. Please reset your          ║
║   password and check your invoice in the customer        ║
║   portal. If the issue persists, please contact          ║
║   support again."                                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

- Return the response string

**Pre-scripted demo responses** (one per ticket, deliberately generic/wrong):
- T1: A vaguely correct but incomplete answer missing tier-specific details
- T2: Generic troubleshooting advice that doesn't address the specific device
- T3: A single-paragraph response that misses 2 of the 3 intents
- T4: Cheerfully provides the wrong policy (onboarding instead of cancellation)
- T5: A polite but tone-deaf response that doesn't recognize the urgency or CFO involvement

Store these as `CHATBOT_DEMO_RESPONSES` dict keyed by ticket ID.

### 2. `run_rag_only(ticket, top_k=3) -> list[dict]`

Calls `search_kb` directly with the ticket subject as the query. Demonstrates what RAG alone returns — no reasoning, no verification.

- Calls `search_kb(ticket["subject"])`
- Prints a styled output:

```
╔══════════════════════════════════════════════════════════╗
║  🔍 RAG-ONLY RETRIEVAL (no reasoning, no verification) ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Query: "Invoice overcharged + device offline..."        ║
║                                                          ║
║  Result 1: KB-003 (score: 0.72)                          ║
║  "Standard Customer Billing & Invoice Disputes..."       ║
║                                                          ║
║  Result 2: KB-002 (score: 0.45)                          ║
║  "GPS Device Troubleshooting..."                         ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  ℹ️  "This is a lookup, not a decision."                ║
╚══════════════════════════════════════════════════════════╝
```

- Returns the list of search results
- The caption **"This is a lookup, not a decision."** must appear at the bottom — it's a key pedagogical label from the design spec

## Output Format

```python
# src/cells/contrast.py

CHATBOT_DEMO_RESPONSES = {
    "T1": "...",
    "T2": "...",
    "T3": "...",
    "T4": "...",
    "T5": "...",
}

def run_frustrated_chatbot(ticket: dict, llm_client=None, demo_response: str | None = None) -> str:
    ...

def run_rag_only(ticket: dict, top_k: int = 3) -> list[dict]:
    ...
```

## Acceptance Criteria

- [ ] Chatbot produces a single generic response with no tool calls
- [ ] Demo responses are deliberately incomplete/wrong for each ticket
- [ ] T4 chatbot demo response gives wrong policy (onboarding instead of cancellation)
- [ ] RAG-only shows raw retrieval results with similarity scores
- [ ] "This is a lookup, not a decision." caption appears in RAG output
- [ ] Both functions use styled print output (box drawing)
- [ ] Module is importable: `from src.cells.contrast import run_frustrated_chatbot, run_rag_only`
