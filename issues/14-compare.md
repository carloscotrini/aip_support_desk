# Issue 14 — COMPARE: Side-by-Side Comparison View

**Wave:** 6 (depends on: #13 CONTRAST, #11 AGENT-LOOP)
**Output:** `src/cells/comparison.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 7, Row 8** and **Section 9: Side-by-Side Comparison**.

## Dependencies

- **Issue #13 (CONTRAST)**: `from src.cells.contrast import run_frustrated_chatbot, CHATBOT_DEMO_RESPONSES`
- **Issue #11 (AGENT-LOOP)**: `from src.agent.loop import run_agent`

## Task

Implement the `run_comparison` function that renders a split-screen HTML view comparing the chatbot response (left) with the agent trace (right), displayed in a Google Colab notebook via `IPython.display`.

## Requirements

### `run_comparison(ticket, chatbot_response=None, agent_state=None) -> None`

If `chatbot_response` or `agent_state` are not provided, the function should run them:
- `chatbot_response = chatbot_response or run_frustrated_chatbot(ticket, demo_response=CHATBOT_DEMO_RESPONSES.get(ticket["ticket_id"]))`
- `agent_state = agent_state or run_agent(ticket, demo_responses=...)` (use demo responses if available)

The function renders styled HTML via `IPython.display.HTML`:

#### Layout

Two-column layout (50/50 split), each in a bordered box:

**Left column: "CHATBOT"**
- Header: "Chatbot Response" with a robot icon
- Subtitle: "No tools, no reasoning loop"
- Body: The plain text chatbot response
- Background: light red/pink tint (suggests inadequacy)

**Right column: "AGENT"**
- Header: "Agent Response" with a gear/brain icon
- Subtitle: "PLAN → ACT → OBSERVE → REFLECT"
- Body: The agent's step trace formatted as a readable list:
  ```
  Step 1 [PLAN]: "Two intents detected: billing + device..."
  Step 2 [ACT]:  search_kb("invoice dispute") → KB-003 (0.72)
  Step 3 [PLAN]: "Need to verify account status..."
  Step 4 [ACT]:  query_customer_db("CUST-1003") → SUSPENDED
  Step 5 [REFLECT]: "Root cause is billing. Replanning."
  ...
  ```
- Final confidence badge: green if ≥ 0.8, yellow if ≥ 0.5, red if < 0.5
- Background: light green tint (suggests competence)

#### Caption

Below the two columns, a centered markdown-style caption:

> *"The chatbot responded. The agent worked."*

#### Styling Requirements

- Use inline CSS (Colab strips `<style>` tags in some contexts)
- Must be projector-safe: readable at low resolution, high contrast
- Use `font-family: monospace` for agent traces
- Responsive: if the viewport is narrow, stack vertically instead of side-by-side
- No external CSS dependencies

### Helper: `_format_agent_trace(agent_state) -> str`

Converts `agent_state["steps_taken"]` into an HTML-formatted trace. Each step should show:
- Step number
- Phase label (PLAN/ACT/OBSERVE/REFLECT)
- For PLAN: the reasoning text
- For ACT: tool name + args (summarized) + result summary
- For REFLECT: confidence change + any replanning note

### Helper: `_confidence_badge(confidence) -> str`

Returns an HTML badge:
- `≥ 0.8`: green badge with "HIGH CONFIDENCE"
- `≥ 0.5`: yellow badge with "MEDIUM CONFIDENCE"
- `< 0.5`: red badge with "LOW CONFIDENCE"

## Output Format

```python
# src/cells/comparison.py

def run_comparison(ticket: dict, chatbot_response: str | None = None, agent_state: dict | None = None) -> None:
    ...

def _format_agent_trace(agent_state: dict) -> str:
    ...

def _confidence_badge(confidence: float) -> str:
    ...
```

## Acceptance Criteria

- [ ] Renders two-column HTML via `IPython.display.HTML`
- [ ] Left column shows chatbot response, right column shows full agent trace
- [ ] Agent trace is step-by-step with phase labels
- [ ] Confidence badge with color coding
- [ ] Caption: "The chatbot responded. The agent worked."
- [ ] Inline CSS only (no external stylesheets)
- [ ] Projector-safe: high contrast, monospace traces, readable at distance
- [ ] Module is importable: `from src.cells.comparison import run_comparison`
