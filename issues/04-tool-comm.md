# Issue 04 — TOOL-COMM: send_email & request_info Tools

**Wave:** 1 (no dependencies)
**Output:** `src/tools/communication.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements two of the five tools from **Section 5: Agent Tools**.

## Task

Create a Python module with two stateless mock tool implementations. These tools only print formatted output — they don't actually send emails or interact with external systems.

## Requirements

### `send_email(to, subject, body) -> dict`

- Prints a formatted email draft with clear visual borders
- Returns a dict: `{"status": "draft_created", "to": to, "subject": subject}`
- Print format should be business-legible, e.g.:

```
╔══════════════════════════════════════════╗
║  📧 EMAIL DRAFT (not sent)              ║
╠══════════════════════════════════════════╣
║  To:      customer@example.com          ║
║  Subject: Re: Invoice Dispute #4471     ║
╠══════════════════════════════════════════╣
║  Dear Ms. Chen,                         ║
║                                         ║
║  [body text here]                       ║
║                                         ║
║  Best regards,                          ║
║  Meridian Fleet Solutions Support       ║
╚══════════════════════════════════════════╝
```

### `request_info(fields_needed) -> dict`

- `fields_needed`: a list of strings describing what information is missing
- Prints a formatted clarification request
- Returns a dict: `{"status": "info_requested", "fields": fields_needed}`
- Print format:

```
╔══════════════════════════════════════════╗
║  ❓ INFORMATION REQUEST                 ║
╠══════════════════════════════════════════╣
║  The agent needs the following info     ║
║  before proceeding:                     ║
║                                         ║
║  1. [field 1]                           ║
║  2. [field 2]                           ║
╚══════════════════════════════════════════╝
```

### Tool Schemas (for LLM function-calling)

Each tool must also export a JSON-compatible schema dict describing its parameters, for use with the LLM's function-calling interface:

```python
SEND_EMAIL_SCHEMA = {
    "name": "send_email",
    "description": "Draft and display an email response to the customer. Does not actually send.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Email body text"}
        },
        "required": ["to", "subject", "body"]
    }
}

REQUEST_INFO_SCHEMA = { ... }
```

## Output Format

```python
# src/tools/communication.py

def send_email(to: str, subject: str, body: str) -> dict:
    ...

def request_info(fields_needed: list[str]) -> dict:
    ...

SEND_EMAIL_SCHEMA = { ... }
REQUEST_INFO_SCHEMA = { ... }
```

## Acceptance Criteria

- [ ] Both functions print formatted, business-legible output
- [ ] Both functions return structured dicts (not just print)
- [ ] Tool schemas are exported as module-level dicts
- [ ] No external dependencies — pure Python + print statements
- [ ] Module is importable: `from src.tools.communication import send_email, request_info, SEND_EMAIL_SCHEMA, REQUEST_INFO_SCHEMA`
