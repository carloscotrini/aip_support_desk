# Issue 11 — AGENT-LOOP: Agent Loop with Confidence Tracking

**Wave:** 5 (depends on: #10 REGISTRY, #03 TICKETS)
**Output:** `src/agent/loop.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 6: Agent Loop Design** and the confidence dashboard described in **Section 7, Row 7** and **Section 8: Key Agentic Moments**.

## Dependencies

- **Issue #10 (REGISTRY)**: `from src.tools.registry import TOOL_SCHEMAS, dispatch_tool`
- **Issue #03 (TICKETS)**: `from src.data.tickets import TICKETS`

Ensure `src/agent/__init__.py` exists (create it if needed).

## Task

Implement the core agent loop that processes customer support tickets through an explicit **PLAN → ACT → OBSERVE → REFLECT** cycle, calling tools via the registry and tracking confidence at every iteration.

## Requirements

### Agent State

```python
agent_state = {
    "ticket": dict,              # the active ticket
    "status": "INVESTIGATING",   # INVESTIGATING | DRAFTING | ESCALATING | RESOLVED
    "confidence": 0.0,           # 0.0–1.0
    "steps_taken": [],           # list of {phase, tool, inputs, outputs, reasoning}
    "context": [],               # accumulated LLM messages
}
```

### The Loop: `run_agent(ticket, llm_client=None, demo_responses=None) -> dict`

```python
def run_agent(ticket: dict, llm_client=None, demo_responses: list[dict] | None = None) -> dict:
    """
    Run the agent loop on a ticket.

    Args:
        ticket: A ticket dict from TICKETS
        llm_client: An LLM client for live mode (if None and no demo_responses, raises error)
        demo_responses: Pre-scripted response list for DEMO_MODE (if provided, uses these instead of LLM)

    Returns:
        The final agent_state dict
    """
```

The loop runs `while agent_state["status"] != "RESOLVED"` with a safety cap of 10 iterations:

#### PHASE 1 — PLAN
- Build a prompt containing: the ticket, all prior steps, and tool schemas
- Call the LLM (or pop next from `demo_responses`) to get a structured JSON response:
  ```python
  {
      "reasoning": "Account suspended 3 days ago — billing is root cause",
      "next_tool": "escalate",
      "tool_args": {"to_person": "Marcus Thiele", "summary": "...", "urgency": "HIGH"},
      "confidence": 0.91,
      "resolution_status": "ESCALATING"
  }
  ```
- Print business-legible trace:
  ```
  [AGENT THINKING] Account suspended 3 days ago — billing is root cause
  [AGENT STATUS]   Confidence: 91% | Status: ESCALATING
  ```

#### PHASE 2 — ACT
- Call `dispatch_tool(next_tool, **tool_args)`
- Log the step to `agent_state["steps_taken"]`
- Print:
  ```
  [AGENT ACTION]   Calling escalate(to_person="Marcus Thiele", urgency="HIGH")
  ```

#### PHASE 3 — OBSERVE
- Append the tool result to `agent_state["context"]`
- Print:
  ```
  [AGENT OBSERVE]  Result: {"status": "escalated", "routed_to": "Marcus Thiele", ...}
  ```

#### PHASE 4 — REFLECT
- Update `agent_state["confidence"]` and `agent_state["status"]` from the LLM response
- If confidence dropped (contradiction detected), print:
  ```
  [AGENT REFLECT]  Confidence dropped: 88% → 31%. Re-planning.
  ```
- If status is `RESOLVED`, print:
  ```
  [AGENT RESOLVED] Ticket resolved in {n} steps. Final confidence: {confidence}%
  ```

### LLM Interaction: `_call_llm(agent_state, llm_client) -> dict`

A helper that:
1. Builds the system prompt (you are a customer support agent for Meridian Fleet Solutions...)
2. Builds the user message from ticket + steps history
3. Passes `TOOL_SCHEMAS` as available tools
4. Calls the LLM and parses the structured JSON response
5. Returns the parsed dict with `reasoning`, `next_tool`, `tool_args`, `confidence`, `resolution_status`

Support both Claude (`anthropic` client) and a simple callable interface. The exact LLM integration details can remain flexible — the key contract is: input = agent_state, output = structured dict.

### Demo Mode

When `demo_responses` is provided, the loop pops from the list instead of calling the LLM. This is the `DEMO_MODE=True` path. The rendering is identical — same print traces, same state updates.

### System Prompt

Write the system prompt for the agent. It should:
- Identify the agent as a Meridian Fleet Solutions support agent
- Instruct it to use the PLAN→ACT→OBSERVE→REFLECT loop
- Require structured JSON output with the 5 fields above
- Instruct it to track confidence honestly and drop it when contradictions arise
- Tell it to escalate when authority limits are exceeded rather than guessing
- Be business-legible (a manager reading it should understand what the agent is told to do)

Store it as `SYSTEM_PROMPT` at module level.

### Confidence Threshold

```python
CONFIDENCE_THRESHOLD = 0.8  # agent only resolves when confidence >= this
MAX_ITERATIONS = 10         # safety cap
```

Both should be module-level constants.

## Output Format

```python
# src/agent/loop.py

SYSTEM_PROMPT = """..."""
CONFIDENCE_THRESHOLD = 0.8
MAX_ITERATIONS = 10

def run_agent(ticket: dict, llm_client=None, demo_responses: list[dict] | None = None) -> dict:
    ...

def _call_llm(agent_state: dict, llm_client) -> dict:
    ...
```

## Acceptance Criteria

- [ ] Loop runs PLAN→ACT→OBSERVE→REFLECT with labeled print traces at each phase
- [ ] Uses `dispatch_tool` from the registry (not direct function calls)
- [ ] Tracks confidence and status in `agent_state`, updates every iteration
- [ ] Stops when `status == "RESOLVED"` or after `MAX_ITERATIONS`
- [ ] Demo mode works by consuming `demo_responses` list
- [ ] Business-legible traces (no jargon — a manager can read them)
- [ ] System prompt is stored as `SYSTEM_PROMPT`
- [ ] Returns final `agent_state` dict with full step history
- [ ] Module is importable: `from src.agent.loop import run_agent, SYSTEM_PROMPT`
