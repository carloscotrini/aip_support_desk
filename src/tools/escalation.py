# src/tools/escalation.py
# Escalation tool for routing issues to the appropriate team member.

from src.data.databases import EMPLOYEE_DIRECTORY

URGENCY_INDICATORS = {
    "STANDARD": "🟢",
    "HIGH": "🟡",
    "CRITICAL": "🔴",
}


def escalate(to_person: str, summary: str, urgency: str, context: str | None = None) -> dict:
    """Escalate a ticket to a specific team member."""
    # Validate urgency
    urgency = urgency.upper()
    if urgency not in URGENCY_INDICATORS:
        urgency = "STANDARD"

    # Look up employee (case-insensitive partial match)
    match = None
    to_lower = to_person.lower()
    for emp in EMPLOYEE_DIRECTORY:
        if to_lower in emp["name"].lower():
            match = emp
            break

    if match is None:
        print(f"⚠️  WARNING: '{to_person}' not found in employee directory. Routing not validated.")
        role = "Unknown"
        authority = "Unknown"
        routing_validated = False
        routed_name = to_person
    else:
        role = match["role"]
        authority = match["authority_scope"]
        routing_validated = True
        routed_name = match["name"]

    indicator = URGENCY_INDICATORS[urgency]
    context_text = context if context else "None"

    W = 58  # inner width between ║ markers
    sep = "═" * W

    def row(text: str) -> None:
        print(f"║ {text:<{W - 1}}║")

    print(f"╔{sep}╗")
    row(f" ESCALATION SUMMARY — {urgency} {indicator}")
    print(f"╠{sep}╣")
    label_w = W - 3  # usable text width inside row after leading space
    route_str = f"{routed_name}, {role}"
    for i, line in enumerate(_wrap(route_str, label_w - 14)):
        row(f" Route To:    {line}" if i == 0 else f"              {line}")
    for i, line in enumerate(_wrap(authority, label_w - 14)):
        row(f" Authority:   {line}" if i == 0 else f"              {line}")
    row(f" Urgency:     {urgency}")
    print(f"╠{sep}╣")
    row(" Summary:")
    for line in _wrap(summary, W - 3):
        row(f" {line}")
    print(f"╠{sep}╣")
    row(" Additional Context:")
    for line in _wrap(context_text, W - 3):
        row(f" {line}")
    print(f"╚{sep}╝")

    return {
        "status": "escalated",
        "routed_to": routed_name,
        "role": role,
        "urgency": urgency,
        "routing_validated": routing_validated,
        "summary": summary,
    }


def _wrap(text: str, width: int) -> list[str]:
    """Simple word-wrap helper."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines or [""]


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
                "description": "Urgency level of the escalation",
            },
            "context": {"type": "string", "description": "Optional additional context (e.g., prior tool results, customer ARR)"},
        },
        "required": ["to_person", "summary", "urgency"],
    },
}
