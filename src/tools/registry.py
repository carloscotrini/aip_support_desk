"""Unified tool registry for the AIP Support Desk agent."""

import json

from src.tools.search_kb import search_kb, SEARCH_KB_SCHEMA
from src.tools.customer_db import query_customer_db, QUERY_CUSTOMER_DB_SCHEMA
from src.tools.communication import send_email, request_info, SEND_EMAIL_SCHEMA, REQUEST_INFO_SCHEMA
from src.tools.escalation import escalate, ESCALATE_SCHEMA

TOOLS = {
    "search_kb": search_kb,
    "query_customer_db": query_customer_db,
    "send_email": send_email,
    "escalate": escalate,
    "request_info": request_info,
}

TOOL_SCHEMAS = [
    SEARCH_KB_SCHEMA,
    QUERY_CUSTOMER_DB_SCHEMA,
    SEND_EMAIL_SCHEMA,
    ESCALATE_SCHEMA,
    REQUEST_INFO_SCHEMA,
]


def dispatch_tool(tool_name: str, **kwargs) -> dict:
    """Look up and call a tool by name, returning its result dict."""
    if tool_name not in TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}

    print(f"[DISPATCH] Calling tool: {tool_name}")
    print(f"[DISPATCH] Arguments: {json.dumps(kwargs, default=str)}")

    try:
        return TOOLS[tool_name](**kwargs)
    except Exception as e:
        return {"error": str(e), "tool": tool_name}


def get_tool_names() -> list[str]:
    """Return the list of available tool names."""
    return list(TOOLS.keys())
