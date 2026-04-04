# Issue 08 — TOOL-DB: query_customer_db Tool

**Wave:** 3 (depends on: #02 MOCK-DB)
**Output:** `src/tools/customer_db.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements the `query_customer_db` tool from **Section 5: Agent Tools**.

## Dependencies

- **Issue #02 (MOCK-DB)** must be complete. Import the database:
  ```python
  from src.data.databases import CUSTOMER_DB
  ```

## Task

Implement the `query_customer_db(customer_id, fields)` tool that looks up customer records from the in-memory mock database.

## Requirements

### `query_customer_db(customer_id, fields=None) -> dict`

1. **Look up** the customer by `customer_id` in `CUSTOMER_DB`
2. If `fields` is provided (a list of strings), return only those fields. If `None`, return all fields.
3. If `customer_id` is not found, return `{"error": "Customer not found", "customer_id": customer_id}`
4. If a requested field doesn't exist, include it as `None` in the result
5. **Always include `customer_id`** in the result even if not in `fields`
6. **Print a business-legible trace**:
   ```
   [TOOL: query_customer_db] Looking up customer CUST-1001...
   [TOOL: query_customer_db] Found: Northgate Logistics (Enterprise, ACTIVE)
   [TOOL: query_customer_db] Fields returned: subscription_tier, account_status, arr
   ```

### Tool Schema

```python
QUERY_CUSTOMER_DB_SCHEMA = {
    "name": "query_customer_db",
    "description": "Look up customer account information from the database. Returns account status, subscription tier, device information, billing history, and other fields.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "The customer ID (e.g., CUST-1001)"},
            "fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of specific fields to return. If omitted, returns all fields."
            }
        },
        "required": ["customer_id"]
    }
}
```

## Output Format

```python
# src/tools/customer_db.py

def query_customer_db(customer_id: str, fields: list[str] | None = None) -> dict:
    ...

QUERY_CUSTOMER_DB_SCHEMA = { ... }
```

## Acceptance Criteria

- [ ] Returns correct data from `CUSTOMER_DB` for valid customer IDs
- [ ] Handles missing customer IDs gracefully with error dict
- [ ] Supports optional field filtering
- [ ] Prints business-legible trace on each call
- [ ] Tool schema exported
- [ ] Module is importable: `from src.tools.customer_db import query_customer_db, QUERY_CUSTOMER_DB_SCHEMA`
