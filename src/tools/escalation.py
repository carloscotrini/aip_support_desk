"""Escalation tool for the AIP Support Desk agent."""


def escalate(reason: str, context_summary: dict) -> dict:
    """Escalate a ticket to a human manager with context summary."""
    width = 50
    border = "═" * width

    print(f"╔{border}╗")
    print(f"║  🚨 ESCALATION{' ' * (width - 16)}║")
    print(f"╠{border}╣")
    print(f"║  Reason: {reason:<{width - 11}}║")
    print(f"╠{border}╣")
    print(f"║  Context Summary:{' ' * (width - 19)}║")

    for key, value in context_summary.items():
        line = f"  {key}: {value}"
        if len(line) > width - 2:
            line = line[: width - 5] + "..."
        print(f"║{line:<{width}}║")

    print(f"╚{border}╝")

    return {
        "status": "escalated",
        "reason": reason,
        "context_summary": context_summary,
    }


ESCALATE_SCHEMA = {
    "name": "escalate",
    "description": "Escalate a ticket to a human manager with a reason and context summary.",
    "parameters": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Reason for escalation (e.g., 'vip_churn_risk', 'sla_breach')",
            },
            "context_summary": {
                "type": "object",
                "description": "Dict of context fields for the manager (e.g., customer_ltv, open_cases_count, sla_status)",
            },
        },
        "required": ["reason", "context_summary"],
    },
}
