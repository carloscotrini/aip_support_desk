# Issue 15 — REENTRY: Stateful Re-entry Cell

**Wave:** 6 (depends on: #11 AGENT-LOOP)
**Output:** `src/cells/reentry.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 7, Row 10: "Next Morning" Re-entry** and **Section 8, Moment 4: Stateful Re-entry**.

## Dependencies

- **Issue #11 (AGENT-LOOP)**: `from src.agent.loop import run_agent`

Ensure `src/cells/__init__.py` exists (create it if needed).

## Task

Implement the "Next Morning" cell that demonstrates stateful persistence — the agent resumes a previously handled ticket with new information, picking up where it left off.

## Requirements

### `resume_agent(prior_state, new_message, llm_client=None, demo_responses=None) -> dict`

1. Takes a `prior_state` (the `agent_state` dict returned by a previous `run_agent` call)
2. Takes a `new_message` string (e.g., Marcus Thiele's reply: "Billing error confirmed, credit issued.")
3. Injects the new message into `prior_state`:
   - Adds it to `steps_taken` as a new step with phase `"EXTERNAL_INPUT"`
   - Resets `status` back to `"INVESTIGATING"` so the loop re-engages
   - Preserves all prior steps and context
4. Calls `run_agent` with the updated state (passing it as the ticket, or re-entering the loop — design this so it reuses the same loop logic)
5. Prints a header:
   ```
   ╔══════════════════════════════════════════════════════════╗
   ║  📬 NEW MESSAGE RECEIVED — Resuming agent...           ║
   ╠══════════════════════════════════════════════════════════╣
   ║  From: Marcus Thiele, Senior Account Manager            ║
   ║  "Billing error confirmed, credit issued."              ║
   ╠══════════════════════════════════════════════════════════╣
   ║  Prior context: 4 steps from previous session           ║
   ║  Resuming PLAN → ACT → OBSERVE → REFLECT loop...       ║
   ╚══════════════════════════════════════════════════════════╝
   ```

### Pre-scripted Demo Content

Provide a default "next morning" scenario:

```python
NEXT_MORNING_MESSAGE = {
    "from": "Marcus Thiele",
    "role": "Senior Account Manager",
    "body": "I've reviewed the Northgate Logistics account. The Q1 billing error has been confirmed — we overcharged $2,340 due to a tier migration glitch. Credit memo has been issued and will appear on their next statement. I've also scheduled a call with their CFO for Thursday to discuss the contract renewal. Please draft a confirmation email to the customer referencing credit memo #CM-2024-0847."
}
```

And a corresponding demo response sequence for the resumed agent (1–2 steps):

```python
REENTRY_DEMO_RESPONSES = [
    {
        "reasoning": "Marcus confirmed the billing error and issued a credit. I need to draft a confirmation email to the customer referencing the credit memo number.",
        "next_tool": "send_email",
        "tool_args": {
            "to": "j.whitfield@northgatelogistics.com",
            "subject": "Re: Q1 Billing Dispute — Credit Memo Issued",
            "body": "..."  # professional email referencing CM-2024-0847
        },
        "confidence": 0.95,
        "resolution_status": "RESOLVED"
    }
]
```

### Pedagogical Print

After the resumed agent completes, print:

```
╔══════════════════════════════════════════════════════════╗
║  💡 KEY INSIGHT: Stateful Persistence                   ║
╠══════════════════════════════════════════════════════════╣
║  The agent resumed with its full prior context:          ║
║  • Remembered all 4 previous steps                       ║
║  • Understood Marcus's reply in context                  ║
║  • Drafted a response referencing prior investigation    ║
║                                                          ║
║  A stateless chatbot would have started from scratch.    ║
╚══════════════════════════════════════════════════════════╝
```

## Output Format

```python
# src/cells/reentry.py

NEXT_MORNING_MESSAGE = { ... }
REENTRY_DEMO_RESPONSES = [ ... ]

def resume_agent(prior_state: dict, new_message: str, llm_client=None, demo_responses: list[dict] | None = None) -> dict:
    ...
```

## Acceptance Criteria

- [ ] Takes a prior `agent_state` and resumes with new information
- [ ] Preserves all prior steps in the resumed state
- [ ] Prints header showing the new message and prior context count
- [ ] Works in demo mode with pre-scripted responses
- [ ] Prints the "Key Insight: Stateful Persistence" box after completion
- [ ] The resumed agent produces a sensible response that references prior context
- [ ] Module is importable: `from src.cells.reentry import resume_agent, NEXT_MORNING_MESSAGE`
