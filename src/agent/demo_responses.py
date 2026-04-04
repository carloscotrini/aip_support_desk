"""Pre-scripted LLM response sequences for DEMO_MODE.

When DEMO_MODE=True, the agent loop pops from these lists instead of
calling the LLM, allowing the full exercise to run without an API key.
"""

DEMO_RESPONSES: dict[str, list[dict]] = {
    # ------------------------------------------------------------------
    # T1 — Happy Path (2 steps)
    # ------------------------------------------------------------------
    "T1": [
        {
            "reasoning": (
                "The customer is asking how to export a monthly mileage report. "
                "I don't yet know their subscription tier or which export options "
                "are available. Let me search the knowledge base for export procedures."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "mileage report export"},
            "confidence": 0.75,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-001 confirms that Pro-tier customers can export mileage reports "
                "as CSV or PDF with up to 90-day date ranges, and scheduled exports "
                "are available. Now I need to verify this customer's subscription tier "
                "to confirm these features apply to them."
            ),
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1002", "fields": ["subscription_tier", "vehicle_count"]},
            "confidence": 0.85,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Confirmed: Pinecrest Haulage is on the Pro plan with 75 vehicles. "
                "All Pro-tier export features apply. I can now draft a clear response "
                "explaining how to access the mileage report export from the dashboard, "
                "including the CSV/PDF options and the scheduled export feature."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "laura.chen@pinecrest-haulage.com",
                "subject": "How to export your monthly mileage report",
                "body": (
                    "Hi Laura,\n\n"
                    "Great news — as a Pro-plan customer, you have full access to mileage "
                    "report exports. Here's how:\n\n"
                    "1. Go to Reports > Mileage in the dashboard.\n"
                    "2. Select your date range (up to 90 days).\n"
                    "3. Click 'Export' and choose CSV or PDF.\n\n"
                    "Tip: You can also set up scheduled exports under Reports > Scheduled "
                    "to have monthly reports emailed automatically.\n\n"
                    "Let me know if you need anything else!\n\n"
                    "Best regards,\nFleetTracker Support"
                ),
            },
            "confidence": 0.95,
            "resolution_status": "RESOLVED",
        },
    ],

    # ------------------------------------------------------------------
    # T2 — Partial Match (3 steps)
    # ------------------------------------------------------------------
    "T2": [
        {
            "reasoning": (
                "A GPS device has stopped pinging for 48+ hours. The driver reports "
                "the truck is running fine, so power loss is unlikely. Let me check "
                "the knowledge base for device troubleshooting procedures."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "device offline GPS troubleshooting"},
            "confidence": 0.55,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-002 covers common causes — cellular dead zones, SIM deactivation, "
                "firmware issues — but explicitly states that hardware fault diagnosis "
                "is outside scope. I need to check the customer database for device "
                "MF-4471's status, last ping time, and warranty information."
            ),
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1003"},
            "confidence": 0.60,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Database confirms device MF-4471 last pinged on 2026-04-02, over 48 "
                "hours ago, status OFFLINE. The driver says the truck has been running, "
                "so power disconnection is unlikely. KB-002 says hardware fault diagnosis "
                "is out of scope and requires escalation. I don't have enough information "
                "to determine if this is a SIM issue, firmware issue, or hardware fault. "
                "I'll draft a response with the troubleshooting steps I can offer and "
                "request additional information for further diagnosis."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "derek.owusu@summit-regional.com",
                "subject": "Re: Device #MF-4471 — troubleshooting steps and next actions",
                "body": (
                    "Hi Derek,\n\n"
                    "I've confirmed that device MF-4471 last reported in on April 2nd "
                    "and is currently showing as offline. Since the truck is running, "
                    "we can rule out a simple power issue. Here are a few things to try:\n\n"
                    "1. Ask the driver to check that the device's LED indicator is lit.\n"
                    "2. Verify the device hasn't been moved or jarred loose from its mount.\n"
                    "3. If possible, have the driver power-cycle the unit (unplug for 30 "
                    "seconds, then reconnect).\n\n"
                    "If none of these resolve it, this may be a hardware or SIM issue that "
                    "requires further diagnosis. Could you let me know:\n"
                    "- Has anything changed on the truck recently (new wiring, dashboard work)?\n"
                    "- Is the device still under warranty?\n\n"
                    "I'll keep this ticket open and escalate to our hardware team if needed.\n\n"
                    "Best regards,\nFleetTracker Support"
                ),
            },
            "confidence": 0.72,
            "resolution_status": "RESOLVED",
        },
    ],

    # ------------------------------------------------------------------
    # T3 — Multi-Intent "Money Shot" (5 steps, 3+ tools)
    # ------------------------------------------------------------------
    "T3": [
        {
            "reasoning": (
                "This ticket has three issues: a $700 billing overcharge, offline devices, "
                "and a DOT compliance report deadline. I need to tackle billing first since "
                "the account appears suspended. Let me search the knowledge base for "
                "invoice dispute procedures."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "invoice dispute billing overcharge"},
            "confidence": 0.50,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-003 outlines the billing dispute process: I can approve credits up to "
                "$500, but this dispute is $700 — that exceeds my authority. Disputes "
                "between $500 and $5,000 route to Marcus Thiele. But first, I need to pull "
                "the customer record to understand the full picture — account status, "
                "devices, and subscription details."
            ),
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1005"},
            "confidence": 0.55,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Customer record confirms: Greenfield Carriers, Pro tier, $54K ARR, "
                "account status SUSPENDED, Q1 billing dispute of $700. Two devices offline. "
                "The suspension is likely tied to the billing dispute. The customer also has "
                "a compliance report due tomorrow. Let me search for device troubleshooting "
                "to address the second issue."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "device troubleshooting offline"},
            "confidence": 0.60,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-002 confirms standard device troubleshooting steps. The devices went "
                "offline April 1st — the same date the account was suspended. This is "
                "likely a suspension side-effect, not a hardware issue. I now have enough "
                "context to draft a response addressing all three issues and explaining "
                "the situation to the customer."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "tom.brennan@greenfield-carriers.com",
                "subject": "Re: Invoice overcharge, device status, and compliance report — action plan",
                "body": (
                    "Hi Tom,\n\n"
                    "Thank you for reaching out. I've reviewed your account and here's "
                    "what I've found across all three issues:\n\n"
                    "1. BILLING: Your Q1 invoice shows a $700 discrepancy. This exceeds "
                    "my direct authority to issue a credit, so I'm escalating it to our "
                    "Senior Account Manager right now. You should hear back within 24 hours.\n\n"
                    "2. DEVICES OFFLINE: Your tracking devices went offline on April 1st. "
                    "This appears to be linked to the account suspension triggered by the "
                    "billing dispute — not a hardware fault. Once the billing issue is "
                    "resolved and the account is reactivated, your devices should come "
                    "back online.\n\n"
                    "3. COMPLIANCE REPORT: I understand your DOT report is due tomorrow. "
                    "I've flagged this as urgent in the escalation so the team prioritizes "
                    "account reactivation. In the meantime, any data collected before "
                    "April 1st should still be available for export.\n\n"
                    "I'm treating this as high priority. Hang tight.\n\n"
                    "Best regards,\nFleetTracker Support"
                ),
            },
            "confidence": 0.80,
            "resolution_status": "DRAFTING",
        },
        {
            "reasoning": (
                "The billing dispute is $700, which exceeds my $500 authority cap. "
                "Greenfield Carriers is a Pro-tier customer with $54K ARR. Per KB-003, "
                "disputes between $500 and $5,000 go to Marcus Thiele (Senior Account "
                "Manager). The account suspension and compliance deadline make this urgent."
            ),
            "next_tool": "escalate",
            "tool_args": {
                "to_person": "Marcus Thiele",
                "summary": (
                    "Pro-tier customer Greenfield Carriers (CUST-1005, $54K ARR) has a "
                    "$700 Q1 billing dispute. Account is SUSPENDED, causing device outages "
                    "and blocking a DOT compliance report due tomorrow. Requires manager "
                    "authority to approve credit and reactivate account."
                ),
                "urgency": "HIGH",
                "context": (
                    "Three interrelated issues: (1) $700 unexplained Q1 invoice increase, "
                    "(2) both tracking devices offline since April 1 due to suspension, "
                    "(3) DOT compliance report due tomorrow requires account data access. "
                    "Customer is frustrated — account reactivation is time-critical."
                ),
            },
            "confidence": 0.92,
            "resolution_status": "RESOLVED",
        },
    ],

    # ------------------------------------------------------------------
    # T4 — Confidence Collapse: THE critical demo moment (4 steps)
    # ------------------------------------------------------------------
    "T4": [
        {
            "reasoning": (
                "Customer is asking about our cancellation policy. Let me search the "
                "knowledge base for cancellation terms and procedures."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "cancellation policy"},
            "confidence": 0.88,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Found relevant document about onboarding which mentions offboarding "
                "procedures. Confidence is good. I'll start drafting a response based on "
                "the offboarding information referenced in KB-004. Let me verify the "
                "customer's account details to personalize the response."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "monica.alvarez@ridgeline-express.com",
                "subject": "Re: Cancellation policy information",
                "body": (
                    "Hi Monica,\n\n"
                    "Thank you for your inquiry. According to our documentation, "
                    "the offboarding process is outlined in Section 7 of the Account "
                    "Lifecycle Manual. I'm pulling up your specific account details "
                    "to confirm which terms apply to your contract.\n\n"
                    "I'll follow up shortly with the complete details.\n\n"
                    "Best regards,\nFleetTracker Support"
                ),
            },
            "confidence": 0.85,
            "resolution_status": "DRAFTING",
        },
        {
            "reasoning": (
                "Wait — I need to verify the customer's tier before sending that draft. "
                "The onboarding guide I found is a general document. Let me check the "
                "customer database first."
            ),
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1004"},
            "confidence": 0.31,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Wait — this customer is on the Basic tier with a $18K ARR contract. "
                "The onboarding guide's offboarding section is just a cross-reference "
                "to the Account Lifecycle Manual — it doesn't contain the actual "
                "cancellation terms. My previous retrieval was wrong. I need to re-query "
                "the knowledge base specifically for contract terms and cancellation "
                "provisions that apply to this customer's tier."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "contract cancellation termination terms"},
            "confidence": 0.45,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-003 and KB-005 provide the contract and cancellation framework. "
                "For a Basic-tier customer: standard contracts require 90-day written "
                "notice for non-renewal, and early termination may incur a fee of 50%% "
                "of remaining contract value. I now have the correct information to draft "
                "an accurate response for Monica."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "monica.alvarez@ridgeline-express.com",
                "subject": "Re: Cancellation policy — corrected details",
                "body": (
                    "Hi Monica,\n\n"
                    "Thank you for your patience. Here are the cancellation terms that "
                    "apply to your account:\n\n"
                    "- **Notice period:** 90 days written notice is required for "
                    "non-renewal.\n"
                    "- **Early termination:** If you cancel before the contract term ends, "
                    "an early termination fee of 50%% of the remaining contract value "
                    "applies.\n"
                    "- **Process:** Submit a written cancellation request to your account "
                    "manager or to support@fleettracker.com.\n\n"
                    "If you'd like to discuss your options or explore whether a plan "
                    "change might be a better fit, I'm happy to connect you with our "
                    "account team.\n\n"
                    "Best regards,\nFleetTracker Support"
                ),
            },
            "confidence": 0.90,
            "resolution_status": "RESOLVED",
        },
    ],

    # ------------------------------------------------------------------
    # T5 — Authority-Boundary Escalation (4 steps)
    # ------------------------------------------------------------------
    "T5": [
        {
            "reasoning": (
                "This is a CFO writing about a $2,340 billing dispute with contract "
                "termination threatened and legal counsel cc'd. This is high-stakes. "
                "Let me search the knowledge base for Enterprise contract terms and "
                "dispute resolution procedures."
            ),
            "next_tool": "search_kb",
            "tool_args": {"query": "Enterprise SLA contract billing dispute"},
            "confidence": 0.65,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "KB-005 covers Enterprise SLA terms. Critical finding: disputes over "
                "$5,000 have a [REDACTED — VP APPROVAL REQUIRED] section, meaning "
                "resolution authority is restricted. KB-003 says C-level executives on "
                "a ticket should be treated as high-priority and Enterprise clients with "
                "ARR over $50K route to Marcus Thiele. But I need to verify the full "
                "customer profile first."
            ),
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1001"},
            "confidence": 0.60,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": (
                "Customer profile confirms: Northgate Logistics, Enterprise tier, "
                "250 vehicles, $180K ARR, contact is James Whitfield (CFO). The dispute "
                "is $2,340 — this exceeds my $500 authority cap. Per KB-003: Enterprise "
                "clients with ARR over $50K route to Marcus Thiele for disputes $500–$5,000. "
                "However, this situation has additional severity factors: the CFO is "
                "personally involved, legal counsel has been cc'd, and contract termination "
                "is explicitly threatened on a $180K account. KB-005 flags C-level contacts "
                "as P1. This goes beyond Marcus's scope — it needs VP-level attention. "
                "Escalating to Priya Nair as CRITICAL."
            ),
            "next_tool": "escalate",
            "tool_args": {
                "to_person": "Priya Nair",
                "summary": (
                    "CRITICAL: Enterprise CFO James Whitfield (Northgate Logistics) "
                    "threatening contract termination over unresolved $2,340 Q1 billing "
                    "overcharge. 250 vehicles, $180K ARR at risk. Legal counsel cc'd. "
                    "Two prior support contacts failed to resolve. Requires VP authority."
                ),
                "urgency": "CRITICAL",
                "context": (
                    "Account: Northgate Logistics (CUST-1001), Enterprise tier, 250 "
                    "vehicles, $180K ARR. CFO James Whitfield reports $2,340 Q1 billing "
                    "overcharge unresolved after two prior inquiries. Has cc'd legal "
                    "counsel and set end-of-week deadline for resolution or contract "
                    "termination. Per KB-003 and KB-005: C-level involvement = P1, "
                    "Enterprise ARR >$50K, dispute exceeds agent $500 cap. Churn risk "
                    "is severe — this is our largest account tier."
                ),
            },
            "confidence": 0.94,
            "resolution_status": "ESCALATING",
        },
        {
            "reasoning": (
                "Escalation to Priya Nair (VP Customer Success) has been routed "
                "successfully with CRITICAL urgency. Given the severity — CFO involvement, "
                "legal threat, $180K ARR at risk — I should not attempt further direct "
                "resolution. The VP needs to handle this personally. Marking as resolved "
                "from my end; the escalation artifact contains all necessary context."
            ),
            "next_tool": "send_email",
            "tool_args": {
                "to": "james.whitfield@northgate-logistics.com",
                "subject": "Re: Q1 billing dispute — escalated to VP Customer Success",
                "body": (
                    "Mr. Whitfield,\n\n"
                    "Thank you for bringing this to our attention. I understand the "
                    "urgency and take this matter very seriously.\n\n"
                    "I have escalated your case directly to Priya Nair, our VP of "
                    "Customer Success, with full context including the $2,340 dispute, "
                    "your prior support interactions, and your timeline. She will be "
                    "reaching out to you personally.\n\n"
                    "You should expect to hear from her within 24 hours. If you need "
                    "immediate assistance in the meantime, please reply to this email.\n\n"
                    "Sincerely,\nFleetTracker Support"
                ),
            },
            "confidence": 0.95,
            "resolution_status": "RESOLVED",
        },
    ],
}


def get_demo_responses(ticket_id: str) -> list[dict]:
    """Return a copy of the demo response sequence for a ticket."""
    return [dict(r) for r in DEMO_RESPONSES[ticket_id]]
