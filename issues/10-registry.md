# Issue 10 — REGISTRY: Tool Registry & LLM Schemas

**Wave:** 4 (depends on: #04 TOOL-COMM, #07 TOOL-RAG, #08 TOOL-DB, #09 TOOL-ESC)
**Output:** `src/tools/registry.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 5: Agent Tools** — specifically the unified `TOOLS` registry and the combined schema list for LLM function-calling.

## Dependencies

All five tools must be complete. Import them:

```python
from src.tools.search_kb import search_kb, SEARCH_KB_SCHEMA
from src.tools.customer_db import query_customer_db, QUERY_CUSTOMER_DB_SCHEMA
from src.tools.communication import send_email, request_info, SEND_EMAIL_SCHEMA, REQUEST_INFO_SCHEMA
from src.tools.escalation import escalate, ESCALATE_SCHEMA
```

## Task

Create a unified tool registry module that:
1. Collects all tool functions into a single dispatch dict
2. Collects all tool schemas into a single list for LLM function-calling
3. Provides a dispatch function that calls the right tool by name

## Requirements

### `TOOLS` — Dispatch Dict

```python
TOOLS = {
    "search_kb":          search_kb,
    "query_customer_db":  query_customer_db,
    "send_email":         send_email,
    "escalate":           escalate,
    "request_info":       request_info,
}
```

### `TOOL_SCHEMAS` — Combined Schema List

A list of all 5 tool schemas, ready to pass directly to the LLM's `tools` parameter:

```python
TOOL_SCHEMAS = [
    SEARCH_KB_SCHEMA,
    QUERY_CUSTOMER_DB_SCHEMA,
    SEND_EMAIL_SCHEMA,
    ESCALATE_SCHEMA,
    REQUEST_INFO_SCHEMA,
]
```

### `dispatch_tool(tool_name, **kwargs) -> dict`

A dispatch function that:
1. Looks up `tool_name` in `TOOLS`
2. Calls it with the provided `kwargs`
3. Returns the tool's result dict
4. If `tool_name` is not found, returns `{"error": f"Unknown tool: {tool_name}"}`
5. Wraps execution in a try/except — on error returns `{"error": str(e), "tool": tool_name}`
6. Prints a dispatch trace:
   ```
   [DISPATCH] Calling tool: search_kb
   [DISPATCH] Arguments: {"query": "mileage report export"}
   ```

### `get_tool_names() -> list[str]`

Returns the list of available tool names (convenience for display/debugging).

## Output Format

```python
# src/tools/registry.py

TOOLS = { ... }
TOOL_SCHEMAS = [ ... ]

def dispatch_tool(tool_name: str, **kwargs) -> dict:
    ...

def get_tool_names() -> list[str]:
    ...
```

## Acceptance Criteria

- [ ] `TOOLS` dict contains all 5 tool functions
- [ ] `TOOL_SCHEMAS` list contains all 5 schemas
- [ ] `dispatch_tool` calls the correct function and returns its result
- [ ] `dispatch_tool` handles unknown tools and exceptions gracefully
- [ ] Prints dispatch trace on each call
- [ ] Module is importable: `from src.tools.registry import TOOLS, TOOL_SCHEMAS, dispatch_tool`
