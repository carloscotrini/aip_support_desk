# Issue 17 — ASSEMBLE: Notebook Integration & End-to-End Testing

**Wave:** 7 (depends on: ALL previous issues #01–#16)
**Output:** `notebook.ipynb`, `tests/test_smoke.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the final assembly described in **Section 7: Notebook Structure** — the 11-section Colab notebook and an end-to-end smoke test.

## Dependencies

All previous issues must be complete:

```python
from src.cells.setup import initialize, DEMO_MODE
from src.data.knowledge_base import KNOWLEDGE_BASE
from src.data.databases import CUSTOMER_DB, EMPLOYEE_DIRECTORY
from src.data.tickets import TICKETS, ACTIVE_TICKET
from src.data.embeddings import load_embeddings
from src.tools.registry import TOOLS, TOOL_SCHEMAS, dispatch_tool
from src.agent.loop import run_agent, SYSTEM_PROMPT
from src.agent.demo_responses import DEMO_RESPONSES, get_demo_responses
from src.cells.contrast import run_frustrated_chatbot, run_rag_only, CHATBOT_DEMO_RESPONSES
from src.cells.comparison import run_comparison
from src.cells.reentry import resume_agent, NEXT_MORNING_MESSAGE, REENTRY_DEMO_RESPONSES
from src.content.reflection_prompts import REFLECTION_PROMPTS_MD, PAUSE_POINTS
```

## Task

### Part 1: Assemble the Jupyter Notebook (`notebook.ipynb`)

Create a Jupyter notebook with 11 sections matching the spec exactly:

| # | Section | Cell Type | What it does |
|---|---------|-----------|-------------|
| 1 | **SETUP** | Code | `initialize(demo_mode=True)` — installs deps, loads embeddings, prints status |
| 2 | **KNOWLEDGE BASE** | Markdown + Code | Markdown intro explaining what the KB is; code cell displays all 5 KB docs |
| 3 | **MOCK DATABASE** | Markdown + Code | Markdown intro; code cell displays `CUSTOMER_DB` (pretty-printed) |
| 4 | **TOOL REGISTRY** | Markdown + Code | Markdown intro listing the 5 tools; code cell shows `TOOL_SCHEMAS` |
| 5 | **THE FRUSTRATED CHATBOT** | Markdown + Code | Markdown: "Let's see what a plain chatbot does..."; code: `run_frustrated_chatbot(ACTIVE_TICKET, demo_response=CHATBOT_DEMO_RESPONSES[ACTIVE_TICKET["ticket_id"]])` |
| 6 | **RAG IN ISOLATION** | Markdown + Code | Markdown: "Now let's add retrieval..."; code: `run_rag_only(ACTIVE_TICKET)` |
| 7 | **THE AGENT LOOP** | Markdown + Code | Markdown: "Now the full agent..."; code: `agent_state = run_agent(ACTIVE_TICKET, demo_responses=get_demo_responses(ACTIVE_TICKET["ticket_id"]))` |
| 8 | **SIDE-BY-SIDE COMPARISON** | Markdown + Code | Markdown: "Let's compare..."; code: `run_comparison(ACTIVE_TICKET)` |
| 9 | **TICKET VARIATIONS** | Markdown + Code | Markdown: "Try different tickets..."; code cell with `ACTIVE_TICKET = TICKETS["T4"]` and instructions to re-run sections 5–8 |
| 10 | **"NEXT MORNING" RE-ENTRY** | Markdown + Code | Markdown: "The next day, Marcus replies..."; code: `resume_agent(agent_state, NEXT_MORNING_MESSAGE["body"], demo_responses=REENTRY_DEMO_RESPONSES)` |
| 11 | **REFLECTION** | Markdown | `REFLECTION_PROMPTS_MD` rendered as markdown |

**Markdown cell guidelines:**
- Each section starts with a `## Section Title` markdown cell
- Include the facilitator pause-point note from `PAUSE_POINTS` as an HTML comment: `<!-- FACILITATOR: ... -->`
- Keep markdown concise — 2–3 sentences max per intro
- Section 9 should show how to change `ACTIVE_TICKET` — the only line participants modify

**Code cell guidelines:**
- Each code cell should be self-contained (import what it needs at the top, or rely on prior cells having run)
- Minimize code — participants should see 3–5 lines per cell, not 30
- The `ACTIVE_TICKET` variable in cell 1 or 9 is the only thing participants change

### Part 2: Smoke Test (`tests/test_smoke.py`)

A test script that verifies the full pipeline works end-to-end in demo mode:

```python
def test_all_tickets_demo_mode():
    """Run all 5 tickets through the agent loop in demo mode."""
    for ticket_id in ["T1", "T2", "T3", "T4", "T5"]:
        ticket = TICKETS[ticket_id]
        responses = get_demo_responses(ticket_id)
        state = run_agent(ticket, demo_responses=responses)
        assert state["status"] == "RESOLVED", f"{ticket_id} did not resolve"
        assert len(state["steps_taken"]) > 0, f"{ticket_id} took no steps"

def test_chatbot_contrast():
    """Verify chatbot demo responses exist for all tickets."""
    ...

def test_rag_only():
    """Verify search_kb returns results for each ticket subject."""
    ...

def test_reentry():
    """Verify stateful re-entry works with demo responses."""
    ...

def test_tool_dispatch():
    """Verify all 5 tools are dispatchable."""
    ...
```

Use `pytest` style. No complex fixtures — just direct calls with demo data.

## Output Format

```
notebook.ipynb          # The assembled Jupyter notebook
tests/
├── __init__.py
└── test_smoke.py       # End-to-end smoke tests
```

## Acceptance Criteria

- [ ] Notebook has exactly 11 sections with markdown + code cells as specified
- [ ] Notebook runs top-to-bottom in demo mode with no API key
- [ ] `ACTIVE_TICKET` is the only variable participants change
- [ ] Facilitator pause points embedded as HTML comments in markdown cells
- [ ] Smoke test covers all 5 tickets in demo mode
- [ ] Smoke test covers chatbot contrast, RAG-only, re-entry, and tool dispatch
- [ ] All tests pass with `pytest tests/test_smoke.py`
- [ ] Notebook is importable/runnable: `jupyter nbconvert --execute notebook.ipynb`
