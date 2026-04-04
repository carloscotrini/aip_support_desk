# Issue 09 — TOOL-ESC: escalate Tool

**Wave:** 3 (depends on: #02 MOCK-DB)
**Output:** `src/tools/escalation.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the `escalate` tool from **Section 5: Agent Tools** and the escalation artifact from **Section 8: Key Agentic Moments (Moment 3)**.

## Dependencies

- **Issue #02 (MOCK-DB)** must be complete. Import the employee directory:
  ```python
  from src.data.databases import EMPLOYEE_DIRECTORY
  ```

## Task

Implement the `escalate(to_person, summary, urgency)` tool that produces a structured escalation artifact and validates routing against the employee directory.

## Requirements

### `escalate(to_person, summary, urgency, context=None) -> dict`

1. **Validate** `to_person` against `EMPLOYEE_DIRECTORY` — find the matching employee by name (case-insensitive partial match is fine)
2. If no match found, print a warning and still produce the artifact with `"routing_validated": False`
3. **Print the structured escalation artifact** exactly as specified in the design:

   ```
   ╔══════════════════════════════════════════════════════════╗
   ║  ESCALATION SUMMARY — [URGENCY LEVEL] [color indicator] ║
   ╠══════════════════════════════════════════════════════════╣
   ║  Route To:    [name], [role]                            ║
   ║  Authority:   [authority_scope]                         ║
   ║  Urgency:     [STANDARD / HIGH / CRITICAL]              ║
   ╠══════════════════════════════════════════════════════════╣
   ║  Summary:                                               ║
   ║  [summary text]                                         ║
   ╠══════════════════════════════════════════════════════════╣
   ║  Additional Context:                                    ║
   ║  [context if provided, or "None"]                       ║
   ╚══════════════════════════════════════════════════════════╝
   ```

4. **Urgency levels**: `"STANDARD"`, `"HIGH"`, `"CRITICAL"`
   - CRITICAL should print with a red indicator (use emoji: 🔴)
   - HIGH with yellow (🟡)
   - STANDARD with green (🟢)

5. **Return** a structured dict:
   ```python
   {
       "status": "escalated",
       "routed_to": "Marcus Thiele",
       "role": "Senior Account Manager",
       "urgency": "HIGH",
       "routing_validated": True,
       "summary": "..."
   }
   ```

### Tool Schema

```python
ESCALATE_SCHEMA = {
    "name": "escalate",
    "description": "Escalate a ticket to a specific team member when the issue exceeds the agent's authority or requires human judgment. Produces a structured escalation artifact.",
    "parameters": {
        "type": "object",
        "properties": {
            "to_person": {"type": "string", "description": "Name of the person to escalate to (e.g., 'Marcus Thiele')"},
            "summary": {"type": "string", "description": "Structured summary of the issue, steps taken, and why escalation is needed"},
            "urgency": {
                "type": "string",
                "enum": ["STANDARD", "HIGH", "CRITICAL"],
                "description": "Urgency level of the escalation"
            },
            "context": {"type": "string", "description": "Optional additional context (e.g., prior tool results, customer ARR)"}
        },
        "required": ["to_person", "summary", "urgency"]
    }
}
```

## Output Format

```python
# src/tools/escalation.py

def escalate(to_person: str, summary: str, urgency: str, context: str | None = None) -> dict:
    ...

ESCALATE_SCHEMA = { ... }
```

## Acceptance Criteria

- [ ] Validates `to_person` against `EMPLOYEE_DIRECTORY`
- [ ] Prints formatted escalation artifact with urgency color indicators
- [ ] Returns structured dict with `routing_validated` flag
- [ ] Handles unknown person gracefully (warning + `routing_validated: False`)
- [ ] CRITICAL/HIGH/STANDARD urgency levels with visual differentiation
- [ ] Tool schema exported
- [ ] Module is importable: `from src.tools.escalation import escalate, ESCALATE_SCHEMA`
