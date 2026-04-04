# src/tools/registry.py
"""
Tool registry — central dispatch for all agent tools.
Collects schemas and provides a single dispatch_tool() entry point.
"""

from src.tools.search_kb import search_kb, SEARCH_KB_SCHEMA
from src.tools.customer_db import query_customer_db, QUERY_CUSTOMER_DB_SCHEMA
from src.tools.communication import send_email, SEND_EMAIL_SCHEMA, request_info, REQUEST_INFO_SCHEMA
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

TOOL_SCHEMAS = [
    SEARCH_KB_SCHEMA,
    QUERY_CUSTOMER_DB_SCHEMA,
    SEND_EMAIL_SCHEMA,
    REQUEST_INFO_SCHEMA,
    ESCALATE_SCHEMA,
    CHECK_SLA_STATUS_SCHEMA,
    CHECK_OPEN_CASES_SCHEMA,
]

_TOOL_FUNCTIONS = {
    "search_kb": search_kb,
    "query_customer_db": query_customer_db,
    "send_email": send_email,
    "request_info": request_info,
    "escalate": escalate,
    "check_sla_status": check_sla_status,
    "check_open_cases": check_open_cases,
}

# Convenience aliases used in brainstorm_summary
_TOOL_ALIASES = {
    "kb_search": "search_kb",
    "db_lookup": "query_customer_db",
    "email_draft": "send_email",
}


def dispatch_tool(tool_name: str, **kwargs) -> dict:
    """Dispatch a tool call by name. Returns the tool's result dict."""
    # Resolve aliases
    canonical = _TOOL_ALIASES.get(tool_name, tool_name)

    fn = _TOOL_FUNCTIONS.get(canonical)
    if fn is None:
        return {"error": f"Unknown tool: {tool_name}"}

    return fn(**kwargs)
