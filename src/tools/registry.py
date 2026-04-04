"""Unified tool registry for the AIP Support Desk agent."""

import json

from src.tools.search_kb import search_kb, SEARCH_KB_SCHEMA
from src.tools.customer_db import query_customer_db, QUERY_CUSTOMER_DB_SCHEMA
from src.tools.communication import send_email, request_info, SEND_EMAIL_SCHEMA, REQUEST_INFO_SCHEMA
from src.tools.escalation import escalate, ESCALATE_SCHEMA


# ---------------------------------------------------------------------------
# Stub tools for check_sla_status and check_open_cases (not yet implemented)
# ---------------------------------------------------------------------------

def check_sla_status(ticket_id: str) -> dict:
    """Check whether a ticket has breached its SLA timers."""
    print(f"[TOOL: check_sla_status] Checking SLA for ticket {ticket_id}...")
    return {"ticket_id": ticket_id, "sla_breached": False, "time_remaining": "4h 12m"}


CHECK_SLA_STATUS_SCHEMA = {
    "name": "check_sla_status",
    "description": "Check whether a ticket has breached its SLA timers.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string", "description": "The ticket ID to check"},
        },
        "required": ["ticket_id"],
    },
}


def check_open_cases(customer_id: str) -> dict:
    """Check if a customer has other active tickets."""
    print(f"[TOOL: check_open_cases] Checking open cases for {customer_id}...")
    return {"customer_id": customer_id, "open_cases": 0, "cases": []}


CHECK_OPEN_CASES_SCHEMA = {
    "name": "check_open_cases",
    "description": "Check if a customer has other active tickets.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "The customer ID to check"},
        },
        "required": ["customer_id"],
    },
}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TOOLS = {
    "search_kb": search_kb,
    "query_customer_db": query_customer_db,
    "send_email": send_email,
    "escalate": escalate,
    "request_info": request_info,
    "check_sla_status": check_sla_status,
    "check_open_cases": check_open_cases,
}

# Convenience aliases used in brainstorm_summary
_TOOL_ALIASES = {
    "kb_search": "search_kb",
    "db_lookup": "query_customer_db",
    "email_draft": "send_email",
}

TOOL_SCHEMAS = [
    SEARCH_KB_SCHEMA,
    QUERY_CUSTOMER_DB_SCHEMA,
    SEND_EMAIL_SCHEMA,
    ESCALATE_SCHEMA,
    REQUEST_INFO_SCHEMA,
    CHECK_SLA_STATUS_SCHEMA,
    CHECK_OPEN_CASES_SCHEMA,
]


def dispatch_tool(tool_name: str, **kwargs) -> dict:
    """Look up and call a tool by name, returning its result dict."""
    # Resolve aliases
    canonical = _TOOL_ALIASES.get(tool_name, tool_name)

    if canonical not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    print(f"[DISPATCH] Calling tool: {canonical}")
    print(f"[DISPATCH] Arguments: {json.dumps(kwargs, default=str)}")

    try:
        return TOOLS[canonical](**kwargs)
    except Exception as e:
        return {"error": str(e), "tool": canonical}


def get_tool_names() -> list[str]:
    """Return the list of available tool names."""
    return list(TOOLS.keys())
