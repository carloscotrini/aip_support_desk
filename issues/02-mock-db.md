# Issue 02 — MOCK-DB: Mock Customer & Employee Databases

**Wave:** 1 (no dependencies)
**Output:** `src/data/databases.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 2 (Fictional Company & Scenario)** database layer and the **Employee Directory**.

## Task

Create a Python module with two in-memory data structures:

1. **CUSTOMER_DB** — a dict keyed by `customer_id` containing customer and device records
2. **EMPLOYEE_DIRECTORY** — a list of dicts representing escalation targets

## Requirements

### CUSTOMER_DB

Must include at least 5 customer records that align with the 5 tickets (T1–T5). Each record should contain:

| Field | Type | Example |
|-------|------|---------|
| `customer_id` | str | `"CUST-1001"` |
| `company_name` | str | `"Northgate Logistics"` |
| `contact_name` | str | `"James Whitfield"` |
| `contact_role` | str | `"CFO"` |
| `subscription_tier` | str | `"Basic"` / `"Pro"` / `"Enterprise"` |
| `account_status` | str | `"ACTIVE"` / `"SUSPENDED"` / `"PENDING"` |
| `arr` | float | `180000.00` |
| `vehicle_count` | int | `250` |
| `devices` | list[dict] | each with `device_id`, `status`, `last_ping` |
| `billing_history` | list[dict] | each with `quarter`, `amount_billed`, `amount_disputed` |

Key data points that tickets depend on:
- **T1 customer**: Active, Basic or Pro tier (affects export features)
- **T2 customer**: Has device `#MF-4471` with `last_ping` 48+ hours ago
- **T3 customer**: Has billing discrepancy + an offline device + Active account
- **T4 customer**: Enterprise tier (so the agent discovers the onboarding doc doesn't apply)
- **T5 customer**: Enterprise, 250 vehicles, $180K ARR, CFO as contact, Q1 billing dispute of $2,340

### EMPLOYEE_DIRECTORY

Three escalation targets, exactly as specified:

| Name | Role | Authority Scope | Trigger Criteria |
|------|------|-----------------|-----------------|
| Dana Okafor | Billing Manager | Disputes under $500 | Standard billing issues |
| Marcus Thiele | Senior Account Manager | Enterprise clients, churn risk, disputes $500–$5,000 | ARR > $50K OR CFO mentioned |
| Priya Nair | VP Customer Success | CRITICAL escalations, VP approval required | Beyond Marcus's authority |

## Output Format

```python
# src/data/databases.py

CUSTOMER_DB = {
    "CUST-1001": { ... },
    # ...
}

EMPLOYEE_DIRECTORY = [
    {
        "name": "Dana Okafor",
        "role": "Billing Manager",
        "authority_scope": "Disputes under $500",
        "trigger_criteria": "Standard billing issues"
    },
    # ...
]
```

## Acceptance Criteria

- [ ] At least 5 customers, one per ticket scenario
- [ ] T5 customer has: Enterprise tier, 250 vehicles, $180K ARR, CFO contact, Q1 dispute of $2,340
- [ ] T2 customer has device `MF-4471` with stale `last_ping`
- [ ] 3 employees with clear authority scopes
- [ ] Module is importable: `from src.data.databases import CUSTOMER_DB, EMPLOYEE_DIRECTORY`
