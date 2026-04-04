# src/tools/customer_db.py
# Tool for querying the in-memory customer database.

from src.data.databases import CUSTOMER_DB


def query_customer_db(customer_id: str, fields: list[str] | None = None) -> dict:
    """Look up customer account information from the database."""
    print(f"[TOOL: query_customer_db] Looking up customer {customer_id}...")

    record = CUSTOMER_DB.get(customer_id)
    if record is None:
        print(f"[TOOL: query_customer_db] Customer {customer_id} not found.")
        return {"error": "Customer not found", "customer_id": customer_id}

    company = record.get("company_name", "Unknown")
    tier = record.get("subscription_tier", "Unknown")
    status = record.get("account_status", "Unknown")
    print(f"[TOOL: query_customer_db] Found: {company} ({tier}, {status})")

    if fields is None:
        print(f"[TOOL: query_customer_db] Fields returned: all")
        return dict(record)

    result = {"customer_id": customer_id}
    for f in fields:
        result[f] = record.get(f)
    returned = [f for f in fields if f != "customer_id"]
    print(f"[TOOL: query_customer_db] Fields returned: {', '.join(returned)}")
    return result


QUERY_CUSTOMER_DB_SCHEMA = {
    "name": "query_customer_db",
    "description": (
        "Look up customer account information from the database. "
        "Returns account status, subscription tier, device information, "
        "billing history, and other fields."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer ID (e.g., CUST-1001)",
            },
            "fields": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Optional list of specific fields to return. "
                    "If omitted, returns all fields."
                ),
            },
        },
        "required": ["customer_id"],
    },
}
