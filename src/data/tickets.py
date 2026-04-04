# src/data/tickets.py
# Customer support tickets (T1–T5) for Meridian Fleet Solutions agentic AI demo.

TICKETS = {
    "T1": {
        "ticket_id": "T1",
        "customer_id": "CUST-1002",
        "subject": "How do I export my monthly mileage report?",
        "body": (
            "Hi there, I'm trying to pull our monthly mileage report for March but "
            "I can't seem to find the export option in the dashboard. We're on the Pro "
            "plan and have about 75 vehicles — could you point me to the right place? "
            "Thanks in advance."
        ),
        "complexity": "Low",
        "expected_tools": ["search_kb", "query_customer_db"],
        "teaching_purpose": "Happy path — every ticket is multi-tool",
    },
    "T2": {
        "ticket_id": "T2",
        "customer_id": "CUST-1003",
        "subject": "Device #MF-4471 stopped pinging 48hrs ago",
        "body": (
            "Our GPS unit MF-4471 went dark about 48 hours ago and hasn't come back "
            "online. The driver says the truck's been running fine so it's not a power "
            "issue. Is this a hardware fault? We need that vehicle tracked — it's on a "
            "long-haul route right now and dispatch is getting nervous."
        ),
        "complexity": "Medium",
        "expected_tools": ["search_kb", "query_customer_db"],
        "teaching_purpose": "Partial KB match forces DB verification",
    },
    "T3": {
        "ticket_id": "T3",
        "customer_id": "CUST-1005",
        "subject": "Invoice overcharged + device offline + compliance report due",
        "body": (
            "I've got three problems and I need them handled TODAY. First, our Q1 "
            "invoice is $700 higher than it should be — we never authorized that "
            "increase. Second, both our tracking devices have been offline since "
            "April 1st and nobody told us. Third, I have a DOT compliance report due "
            "TOMORROW and I can't pull the data because our account appears to be "
            "suspended. This is unacceptable."
        ),
        "complexity": "High",
        "expected_tools": ["search_kb", "query_customer_db", "send_email", "escalate"],
        "teaching_purpose": "Multi-intent — the \"money shot\" 3+ tool chain",
    },
    "T4": {
        "ticket_id": "T4",
        "customer_id": "CUST-1004",
        "subject": "Need info on cancellation policy",
        "body": (
            "Hi, could you send me the details of your cancellation policy? We're "
            "evaluating our vendor contracts and I just need to know the terms. Thanks."
        ),
        "complexity": "Mismatch",
        "expected_tools": ["search_kb", "query_customer_db", "search_kb"],
        "teaching_purpose": "Confidence collapse — agent catches wrong retrieval",
    },
    "T5": {
        "ticket_id": "T5",
        "customer_id": "CUST-1001",
        "subject": "Enterprise CFO threatening contract termination over Q1 billing",
        "body": (
            "This is James Whitfield, CFO of Northgate Logistics. Our Q1 invoice "
            "shows a $2,340 overcharge that has not been resolved despite two prior "
            "inquiries. We manage 250 vehicles through your platform at $180K ARR. "
            "If this is not corrected with a written explanation by end of week, we "
            "will be initiating contract termination. I have cc'd our legal counsel."
        ),
        "complexity": "Critical",
        "expected_tools": ["search_kb", "query_customer_db", "escalate"],
        "teaching_purpose": "Authority-boundary escalation with structured artifact",
    },
}

# Default demo ticket — T3 for maximum visual impact (3+ tool chain with escalation)
ACTIVE_TICKET = TICKETS["T3"]
