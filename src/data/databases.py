# src/data/databases.py
# Mock customer database and employee directory for Meridian Fleet Solutions support desk.

CUSTOMER_DB = {
    "CUST-1001": {
        "customer_id": "CUST-1001",
        "company_name": "Northgate Logistics",
        "contact_name": "James Whitfield",
        "contact_role": "CFO",
        "subscription_tier": "Enterprise",
        "account_status": "ACTIVE",
        "arr": 180000.00,
        "vehicle_count": 250,
        "devices": [
            {"device_id": "MF-9010", "status": "ONLINE", "last_ping": "2026-04-04T08:12:00Z"},
            {"device_id": "MF-9011", "status": "ONLINE", "last_ping": "2026-04-04T07:55:00Z"},
        ],
        "billing_history": [
            {"quarter": "Q4-2025", "amount_billed": 45000.00, "amount_disputed": 0.00},
            {"quarter": "Q1-2026", "amount_billed": 47340.00, "amount_disputed": 2340.00},
        ],
    },
    "CUST-1002": {
        "customer_id": "CUST-1002",
        "company_name": "Pinecrest Haulage",
        "contact_name": "Laura Chen",
        "contact_role": "Fleet Manager",
        "subscription_tier": "Pro",
        "account_status": "ACTIVE",
        "arr": 42000.00,
        "vehicle_count": 75,
        "devices": [
            {"device_id": "MF-3300", "status": "ONLINE", "last_ping": "2026-04-04T09:01:00Z"},
            {"device_id": "MF-3301", "status": "ONLINE", "last_ping": "2026-04-04T08:47:00Z"},
        ],
        "billing_history": [
            {"quarter": "Q4-2025", "amount_billed": 10500.00, "amount_disputed": 0.00},
            {"quarter": "Q1-2026", "amount_billed": 10500.00, "amount_disputed": 0.00},
        ],
    },
    "CUST-1003": {
        "customer_id": "CUST-1003",
        "company_name": "Summit Regional Transport",
        "contact_name": "Derek Owusu",
        "contact_role": "Operations Director",
        "subscription_tier": "Pro",
        "account_status": "ACTIVE",
        "arr": 68000.00,
        "vehicle_count": 120,
        "devices": [
            {"device_id": "MF-4471", "status": "OFFLINE", "last_ping": "2026-04-02T06:33:00Z"},
            {"device_id": "MF-4472", "status": "ONLINE", "last_ping": "2026-04-04T08:20:00Z"},
        ],
        "billing_history": [
            {"quarter": "Q4-2025", "amount_billed": 17000.00, "amount_disputed": 0.00},
            {"quarter": "Q1-2026", "amount_billed": 17000.00, "amount_disputed": 0.00},
        ],
    },
    "CUST-1004": {
        "customer_id": "CUST-1004",
        "company_name": "Ridgeline Express",
        "contact_name": "Monica Alvarez",
        "contact_role": "IT Administrator",
        "subscription_tier": "Basic",
        "account_status": "ACTIVE",
        "arr": 18000.00,
        "vehicle_count": 30,
        "devices": [
            {"device_id": "MF-5580", "status": "ONLINE", "last_ping": "2026-04-04T07:45:00Z"},
        ],
        "billing_history": [
            {"quarter": "Q4-2025", "amount_billed": 4500.00, "amount_disputed": 0.00},
            {"quarter": "Q1-2026", "amount_billed": 4500.00, "amount_disputed": 0.00},
        ],
    },
    "CUST-1005": {
        "customer_id": "CUST-1005",
        "company_name": "Greenfield Carriers",
        "contact_name": "Tom Brennan",
        "contact_role": "Logistics Manager",
        "subscription_tier": "Pro",
        "account_status": "SUSPENDED",
        "arr": 54000.00,
        "vehicle_count": 95,
        "devices": [
            {"device_id": "MF-6200", "status": "OFFLINE", "last_ping": "2026-04-01T14:22:00Z"},
            {"device_id": "MF-6201", "status": "OFFLINE", "last_ping": "2026-04-01T14:20:00Z"},
        ],
        "billing_history": [
            {"quarter": "Q4-2025", "amount_billed": 13500.00, "amount_disputed": 0.00},
            {"quarter": "Q1-2026", "amount_billed": 14200.00, "amount_disputed": 700.00},
        ],
    },
}
"""
Ticket-to-customer mapping:
  T1 (mileage export)        → CUST-1002  Pro tier, ACTIVE — affects export features
  T2 (device #MF-4471 offline) → CUST-1003  has MF-4471 with last_ping 48+ hrs ago
  T3 (billing + offline + compliance) → CUST-1005  billing discrepancy, offline devices, SUSPENDED
  T4 (cancellation policy RAG trap) → CUST-1004  Basic tier (onboarding doc mismatch)
       — but also test with CUST-1001 Enterprise to show policy doesn't apply
  T5 (enterprise escalation) → CUST-1001  Enterprise, 250 vehicles, $180K ARR, CFO, Q1 dispute $2,340
"""


EMPLOYEE_DIRECTORY = [
    {
        "name": "Dana Okafor",
        "role": "Billing Manager",
        "authority_scope": "Disputes under $500",
        "trigger_criteria": "Standard billing issues",
    },
    {
        "name": "Marcus Thiele",
        "role": "Senior Account Manager",
        "authority_scope": "Enterprise clients, churn risk, disputes $500–$5,000",
        "trigger_criteria": "ARR > $50K OR CFO mentioned",
    },
    {
        "name": "Priya Nair",
        "role": "VP Customer Success",
        "authority_scope": "CRITICAL escalations, VP approval required",
        "trigger_criteria": "Beyond Marcus's authority",
    },
]
