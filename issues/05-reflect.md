# Issue 05 — REFLECT: Reflection Prompts & Facilitator Notes

**Wave:** 1 (no dependencies)
**Output:** `src/content/reflection_prompts.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 7, Row 11: Reflection Prompts** and addresses **Open Question OQ-4** (facilitator notes).

## Task

Create a Python module containing:
1. Markdown-formatted reflection/discussion prompts for the end of the exercise
2. Inline facilitator pause-point notes for each notebook section

These will be rendered in Colab markdown cells via `IPython.display.Markdown`.

## Requirements

### Reflection Prompts (end-of-exercise discussion)

Write 5–7 discussion questions that help managers connect the exercise to their business context. They should progress from concrete observation to strategic implication:

1. **Observation** — "What did the agent do differently from the chatbot when handling T3?"
2. **Mechanism** — "Why did the agent need to call multiple tools? Could a chatbot have done the same?"
3. **Self-correction** — "What happened when the agent retrieved the wrong document in T4? How did it recover?"
4. **Authority** — "How did the agent decide to escalate in T5 rather than attempting a resolution?"
5. **Business impact** — "Where in your organization could an agentic system like this create the most value?"
6. **Risk** — "What risks do you see in deploying an agent that makes autonomous decisions in customer-facing scenarios?"
7. **Next steps** — "What would you need to evaluate before piloting agentic AI in your team?"

### Facilitator Pause Points (per notebook section)

Write a brief facilitator note for each of the 11 notebook sections. Format: a dict keyed by section number with a short instruction for when to pause and what to highlight.

```python
PAUSE_POINTS = {
    1: "Setup — no pause needed, just ensure everyone's cells run",
    2: "KB — Ask: 'Notice anything missing from these documents?'",
    5: "Chatbot — PAUSE HERE. Ask participants to read the response. 'Would you trust this answer?'",
    7: "Agent Loop — This is the core. Walk through the trace line by line.",
    # ...
}
```

## Output Format

```python
# src/content/reflection_prompts.py

# Markdown string for the final reflection cell
REFLECTION_PROMPTS_MD = """
## Discussion Questions
...
"""

# Facilitator notes keyed by notebook section number
PAUSE_POINTS = {
    1: "...",
    2: "...",
    # ...
}
```

## Acceptance Criteria

- [ ] 5–7 discussion questions progressing from observation to strategy
- [ ] Pause points for all 11 notebook sections
- [ ] All text is business-legible (no jargon, no code references)
- [ ] Markdown renders cleanly in Colab
- [ ] Module is importable: `from src.content.reflection_prompts import REFLECTION_PROMPTS_MD, PAUSE_POINTS`
