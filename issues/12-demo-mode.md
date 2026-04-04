# Issue 12 — DEMO-MODE: Pre-scripted Demo Responses

**Wave:** 6 (depends on: #11 AGENT-LOOP, #03 TICKETS)
**Output:** `src/agent/demo_responses.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the `DEMO_MODE` scripted responses described in **Section 6: Agent Loop Design** and the key moments in **Section 8**.

## Dependencies

- **Issue #11 (AGENT-LOOP)**: The `run_agent` function accepts `demo_responses: list[dict]`. This issue provides those lists.
- **Issue #03 (TICKETS)**: Ticket definitions for reference.

## Task

Create pre-scripted LLM response sequences for all 5 tickets so the exercise works without an API key when `DEMO_MODE=True`.

## Requirements

Each ticket needs a list of structured response dicts, one per agent loop iteration. Each dict has the same schema the LLM would produce:

```python
{
    "reasoning": str,          # business-legible explanation
    "next_tool": str,          # tool name from registry
    "tool_args": dict,         # kwargs for the tool
    "confidence": float,       # 0.0–1.0
    "resolution_status": str   # INVESTIGATING | DRAFTING | ESCALATING | RESOLVED
}
```

### T1 — Happy Path (2 steps)

1. Search KB for "mileage report export" → finds KB-001 (high confidence)
2. Query customer DB to confirm subscription tier → resolve with email draft

### T2 — Partial Match (3 steps)

1. Search KB for "device offline" → finds KB-002 (partial match, medium confidence)
2. Query customer DB for device MF-4471 status → confirms last_ping 48+ hrs ago
3. Reasoning concludes: not enough info for hardware fault diagnosis → request_info or draft response with caveats

### T3 — Multi-Intent "Money Shot" (4–5 steps)

1. Search KB for "invoice dispute" → finds KB-003
2. Query customer DB → discovers billing discrepancy + offline device
3. Search KB for "device troubleshooting" → finds KB-002
4. Draft email addressing multiple issues → send_email
5. Escalate billing portion exceeding $500 cap → escalate to Dana Okafor or Marcus Thiele

### T4 — Confidence Collapse (**THE critical demo moment**, 4 steps)

1. Search KB for "cancellation policy" → **retrieves KB-004** (onboarding doc) with **confidence 0.88** ← THE TRAP
2. Start drafting based on wrong doc → confidence still high
3. Query customer DB → discovers **Enterprise tier** — onboarding doc doesn't apply → **confidence collapses to 0.31**
4. Re-search KB with corrected query → finds KB-003 or KB-005 → recovers, resolves

**This sequence must be exactly right** — it's the most important pedagogical moment. The reasoning text should be vivid:
- Step 1: `"Found relevant document about onboarding which mentions offboarding procedures. Confidence is good."`
- Step 3: `"Wait — this customer is on Enterprise tier. The onboarding guide's offboarding section doesn't apply to Enterprise contracts. My previous retrieval was wrong. I need to re-query."`

### T5 — Authority-Boundary Escalation (3–4 steps)

1. Search KB → finds KB-005 with `[REDACTED — VP APPROVAL REQUIRED]`
2. Query customer DB → discovers 250 vehicles, $180K ARR, CFO as contact
3. Reasoning: dispute is $2,340 (exceeds $500 cap), Enterprise client with churn risk, CFO involved → CRITICAL escalation
4. Escalate to Priya Nair with full structured artifact, urgency=CRITICAL

### Module Structure

```python
DEMO_RESPONSES = {
    "T1": [ ... ],  # list of response dicts
    "T2": [ ... ],
    "T3": [ ... ],
    "T4": [ ... ],
    "T5": [ ... ],
}
```

### Convenience Function

```python
def get_demo_responses(ticket_id: str) -> list[dict]:
    """Return a copy of the demo response sequence for a ticket."""
    return [dict(r) for r in DEMO_RESPONSES[ticket_id]]
```

Returns a copy so the agent loop can pop from it without mutating the original.

## Output Format

```python
# src/agent/demo_responses.py

DEMO_RESPONSES = {
    "T1": [ {...}, {...} ],
    "T2": [ {...}, {...}, {...} ],
    "T3": [ {...}, {...}, {...}, {...}, {...} ],
    "T4": [ {...}, {...}, {...}, {...} ],
    "T5": [ {...}, {...}, {...}, {...} ],
}

def get_demo_responses(ticket_id: str) -> list[dict]:
    ...
```

## Acceptance Criteria

- [ ] All 5 tickets have complete pre-scripted response sequences
- [ ] T4 explicitly shows confidence 0.88 → 0.31 → recovery (the RAG trap moment)
- [ ] T5 escalation includes CRITICAL urgency to Priya Nair
- [ ] T3 uses 3+ tools in sequence (the "money shot")
- [ ] All `reasoning` text is business-legible (a manager can read and understand it)
- [ ] `tool_args` match the actual tool function signatures
- [ ] `get_demo_responses` returns a copy (not a reference)
- [ ] Module is importable: `from src.agent.demo_responses import DEMO_RESPONSES, get_demo_responses`
