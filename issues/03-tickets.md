# Issue 03 — TICKETS: Ticket Definitions (T1–T5)

**Wave:** 1 (soft dependency on #02 for consistent customer IDs)
**Output:** `src/data/tickets.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 4: Customer Tickets**.

## Task

Create a Python module defining the 5 customer support tickets as a `TICKETS` dict keyed by ticket ID.

## Requirements

Each ticket is a dict with these fields:

| Field | Type | Description |
|-------|------|-------------|
| `ticket_id` | str | `"T1"` through `"T5"` |
| `customer_id` | str | Must match a key in `CUSTOMER_DB` from `src/data/databases.py` |
| `subject` | str | One-line ticket subject |
| `body` | str | Full ticket text as the customer wrote it (2–5 sentences, realistic tone) |
| `complexity` | str | `"Low"` / `"Medium"` / `"High"` / `"Mismatch"` / `"Critical"` |
| `expected_tools` | list[str] | Tools the agent should call for this ticket |
| `teaching_purpose` | str | One-line description of what this ticket demonstrates |

### Ticket Specifications

| ID | Subject | Complexity | Expected Tools | Teaching Purpose |
|----|---------|-----------|---------------|-----------------|
| **T1** | "How do I export my monthly mileage report?" | Low | `["search_kb", "query_customer_db"]` | Happy path — every ticket is multi-tool |
| **T2** | "Device #MF-4471 stopped pinging 48hrs ago" | Medium | `["search_kb", "query_customer_db"]` | Partial KB match forces DB verification |
| **T3** | "Invoice overcharged + device offline + compliance report due" | High | `["search_kb", "query_customer_db", "send_email", "escalate"]` | Multi-intent — the "money shot" 3+ tool chain |
| **T4** | "Need info on cancellation policy" | Mismatch | `["search_kb", "query_customer_db", "search_kb"]` | Confidence collapse — agent catches wrong retrieval |
| **T5** | "Enterprise CFO threatening contract termination over Q1 billing" | Critical | `["search_kb", "query_customer_db", "escalate"]` | Authority-boundary escalation with structured artifact |

### Ticket body tone guidelines
- T1: Polite, straightforward question
- T2: Slightly frustrated, mentions specific device ID and timeframe
- T3: Stressed, multiple issues crammed into one message, mentions deadline
- T4: Neutral inquiry, short
- T5: Formal/terse, CFO cc'd, mentions contract termination, specific dollar amounts

## Output Format

```python
# src/data/tickets.py

TICKETS = {
    "T1": {
        "ticket_id": "T1",
        "customer_id": "CUST-...",
        "subject": "...",
        "body": "...",
        "complexity": "Low",
        "expected_tools": ["search_kb", "query_customer_db"],
        "teaching_purpose": "Happy path — every ticket is multi-tool"
    },
    # ... T2 through T5
}

# Default demo ticket
ACTIVE_TICKET = TICKETS["T3"]
```

## Acceptance Criteria

- [ ] 5 tickets with realistic, varied customer tones
- [ ] `customer_id` values are consistent with `src/data/databases.py`
- [ ] T3 is set as `ACTIVE_TICKET` (default demo ticket)
- [ ] Each ticket's `expected_tools` matches the design spec
- [ ] Module is importable: `from src.data.tickets import TICKETS, ACTIVE_TICKET`
