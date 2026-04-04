# AIP Support Desk

An interactive Jupyter notebook exercise for teaching **agentic AI** concepts. Participants run a simulated customer support desk for Meridian Fleet Solutions and compare a plain chatbot, RAG-only retrieval, and a full agent loop.

## Quick start

```bash
# 1. Install dependencies
pip install numpy sentence-transformers scikit-learn pytest jupyter

# 2. Run the notebook
jupyter notebook notebook.ipynb
```

Then run each cell top-to-bottom. Everything works in **demo mode** — no API key needed.

## Running tests

```bash
pytest tests/test_smoke.py -v
```

## Running the notebook headless

```bash
jupyter nbconvert --to notebook --execute notebook.ipynb
```

## What's in the notebook

| Section | What it does |
|---------|-------------|
| 1. Setup | Load embeddings, verify environment |
| 2. Knowledge Base | Browse the 5 support documents |
| 3. Mock Database | Customer records and employee directory |
| 4. Tool Registry | The 7 tools the agent can call |
| 5. Frustrated Chatbot | Plain chatbot response (no tools) |
| 6. RAG in Isolation | Retrieval only (no reasoning) |
| 7. Agent Loop | Full PLAN-ACT-OBSERVE-REFLECT cycle |
| 8. Comparison | Side-by-side chatbot vs. agent |
| 9. Ticket Variations | Change `ACTIVE_TICKET` and re-run 5–8 |
| 10. Re-Entry | Next-morning stateful persistence demo |
| 11. Reflection | Discussion prompts for group debrief |

## Trying different tickets

In Section 9, change the ticket ID to explore different scenarios:

| Ticket | Complexity | What it demonstrates |
|--------|-----------|---------------------|
| T1 | Low | Happy path — multi-tool resolution |
| T2 | Medium | Partial KB match, DB verification |
| T3 | High | Multi-intent "money shot" (default) |
| T4 | Mismatch | Confidence collapse, self-correction |
| T5 | Critical | Authority-boundary escalation |

## Live mode (optional)

To use a real LLM instead of pre-scripted responses, change `demo_mode=False` in the setup cell and provide an Anthropic API key:

```bash
pip install anthropic
```
