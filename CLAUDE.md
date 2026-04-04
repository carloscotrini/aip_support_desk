# AIP Support Desk — Agent Context

## What this is

An interactive Jupyter notebook exercise for teaching **agentic AI** concepts. Participants run a simulated customer support desk for **Meridian Fleet Solutions** (a fleet management SaaS company) and compare a plain chatbot, RAG-only retrieval, and a full agent loop.

The notebook runs entirely in **demo mode** (pre-scripted responses, no API key needed).

## Project structure

```
notebook.ipynb              # 11-section assembled notebook (the deliverable)
src/
  cells/
    setup.py                # initialize(demo_mode=True), DEMO_MODE flag
    contrast.py             # run_frustrated_chatbot(), run_rag_only(), CHATBOT_DEMO_RESPONSES
    comparison.py           # run_comparison() — side-by-side HTML view
    reentry.py              # resume_agent(), NEXT_MORNING_MESSAGE, REENTRY_DEMO_RESPONSES
  content/
    reflection_prompts.py   # REFLECTION_PROMPTS_MD, PAUSE_POINTS (dict keyed 1–11)
  data/
    knowledge_base.py       # KNOWLEDGE_BASE (5 docs, KB-001 to KB-005)
    databases.py            # CUSTOMER_DB (5 customers), EMPLOYEE_DIRECTORY (3 employees)
    tickets.py              # TICKETS (T1–T5), ACTIVE_TICKET (default: T3)
    embeddings.py           # load_embeddings(), compute_embeddings()
    kb_embeddings.npy       # Pre-computed embeddings (all-MiniLM-L6-v2)
    kb_chunks.json          # Chunk metadata for KB docs
  agent/
    loop.py                 # run_agent(), SYSTEM_PROMPT, CONFIDENCE_THRESHOLD, MAX_ITERATIONS
    demo_responses.py       # DEMO_RESPONSES, get_demo_responses(ticket_id)
  tools/
    registry.py             # TOOLS, TOOL_SCHEMAS, dispatch_tool(), get_tool_names()
    search_kb.py            # search_kb() — semantic search over KB embeddings
    customer_db.py          # query_customer_db()
    communication.py        # send_email(), request_info()
    escalation.py           # escalate()
tests/
  test_smoke.py             # 5 pytest tests (all-tickets, chatbot, RAG, reentry, tool dispatch)
issues/                     # Issue specs (01–17) used during development
```

## Key patterns

- **Demo mode**: All functions accept `demo_responses=` parameter for offline/deterministic execution
- **Agent loop**: PLAN → ACT → OBSERVE → REFLECT cycle with confidence tracking (0–1 scale, threshold 0.8)
- **Tool dispatch**: `dispatch_tool(name, **kwargs)` resolves aliases and calls the tool
- **Tickets**: T1 (easy) → T5 (critical escalation). T3 is the default "money shot" demo
- **Stateful re-entry**: `resume_agent()` mutates the state dict in-place (same object reference)

## Running

```bash
# Run tests
pytest tests/test_smoke.py -v

# Execute notebook end-to-end
jupyter nbconvert --to notebook --execute notebook.ipynb
```

## Dependencies

- numpy, sentence-transformers, scikit-learn (for embeddings)
- anthropic (only needed for live mode, not demo mode)
- pytest (for tests)

## Common gotchas

- `resume_agent()` mutates `prior_state` in-place — if comparing step counts before/after, capture `len(state["steps_taken"])` before calling it
- `ACTIVE_TICKET` in `tickets.py` is a module-level variable; the notebook re-assigns it in Section 9
- Tool aliases exist: `kb_search` → `search_kb`, `db_lookup` → `query_customer_db`, `email_draft` → `send_email`
- The registry has 7 tools (not 5) — includes `check_sla_status` and `check_open_cases` stubs
