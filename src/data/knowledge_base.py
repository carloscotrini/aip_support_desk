# src/data/knowledge_base.py
"""
Knowledge Base documents for Meridian Fleet Solutions support desk.

Five internal wiki-style documents used by the support agent via RAG retrieval.
Each document is designed with specific pedagogical roles — perfect matches,
partial matches, authority gaps, adversarial traps, and redacted sections.
"""

KNOWLEDGE_BASE = [
    {
        "doc_id": "KB-001",
        "title": "Exporting Reports: Mileage, Fuel & Compliance",
        "content": (
            "Meridian Fleet Solutions — Internal Support Wiki\n"
            "Document: Exporting Reports: Mileage, Fuel & Compliance\n"
            "Last updated: 2026-03-15\n\n"

            "Overview\n"
            "Meridian's reporting engine allows fleet operators to generate and export "
            "mileage, fuel consumption, and regulatory compliance reports directly from "
            "the Fleet Dashboard. Reports can be exported as PDF, CSV, or Excel files "
            "depending on the customer's subscription tier.\n\n"

            "Step-by-Step Export Instructions\n"
            "1. Log in to the Meridian Fleet Dashboard at dashboard.meridianfleet.io.\n"
            "2. Navigate to Reports > Fleet Analytics from the left sidebar.\n"
            "3. Select the report type: Mileage Summary, Fuel Usage, or Compliance Audit.\n"
            "4. Choose the date range. Monthly reports default to the previous calendar month.\n"
            "5. Click 'Generate Report'. Processing typically takes 10–30 seconds depending "
            "on fleet size.\n"
            "6. Once generated, click the 'Export' button in the top-right corner of the "
            "report viewer.\n"
            "7. Select your preferred format and confirm the download.\n\n"

            "Subscription Tier Differences\n"
            "- Basic Plan: CSV export only. Reports limited to mileage summaries. "
            "Maximum date range of 30 days per export.\n"
            "- Pro Plan: CSV and PDF export. Includes mileage, fuel, and basic compliance "
            "reports. Date range up to 90 days. Scheduled exports available (weekly/monthly "
            "auto-email).\n"
            "- Enterprise Plan: All formats including Excel with pivot tables. Full compliance "
            "audit reports with DOT/FMCSA formatting. Unlimited date range. API access for "
            "programmatic export. Custom report templates and white-labeling.\n\n"

            "Common Issues\n"
            "- 'Export button greyed out': The report has not finished generating. Wait for "
            "the progress bar to complete before attempting export.\n"
            "- 'Format not available': Your subscription tier does not support this format. "
            "Contact your account manager to discuss upgrading.\n"
            "- 'Data appears incomplete': Vehicles that were offline during the reporting "
            "period will show gaps. Check device connectivity status in the Devices panel.\n\n"

            "For questions about report customization or export issues not covered here, "
            "submit a support ticket referencing this document (KB-001)."
        ),
    },
    {
        "doc_id": "KB-002",
        "title": "GPS Device Troubleshooting: Offline & Signal Loss",
        "content": (
            "Meridian Fleet Solutions — Internal Support Wiki\n"
            "Document: GPS Device Troubleshooting: Offline & Signal Loss\n"
            "Last updated: 2026-02-28\n\n"

            "Overview\n"
            "Meridian GPS tracking devices (models MF-4000 and MF-5000 series) communicate "
            "via cellular LTE with GPS positioning. Devices ping the Meridian cloud every "
            "60 seconds under normal operation. This document covers troubleshooting steps "
            "when a device shows as 'Offline' or reports intermittent signal loss.\n\n"

            "Common Causes of Offline Status\n"
            "1. Cellular dead zones: Vehicles operating in rural areas, tunnels, or "
            "underground parking may temporarily lose cellular connectivity. The device "
            "will buffer up to 72 hours of location data and upload when signal is restored.\n"
            "2. Power disconnection: If the device is hardwired to the vehicle battery, check "
            "that the ignition wire and constant-power wire are both connected. A blown fuse "
            "on the vehicle's accessory circuit is the most common power issue.\n"
            "3. SIM card deactivation: Each device ships with an embedded SIM. If the "
            "account is more than 60 days past due, SIM cards are bulk-deactivated. Verify "
            "account standing before troubleshooting further.\n"
            "4. Firmware issue: Devices on firmware versions below 3.2.1 have a known bug "
            "causing phantom disconnects. Check the device firmware version in the admin panel "
            "under Devices > [Device ID] > Info.\n\n"

            "Troubleshooting Steps\n"
            "Step 1: Check the device's last known ping time in the Dashboard under "
            "Devices > Status. If the last ping was within 72 hours, the device may simply "
            "be in a dead zone and buffering data.\n"
            "Step 2: Verify the customer's account status and payment history. Deactivated "
            "SIMs require account reactivation before the device will reconnect.\n"
            "Step 3: Ask the customer to perform a manual power cycle — disconnect the device "
            "from power for 30 seconds, then reconnect. The device LED should blink green "
            "three times upon successful reboot.\n"
            "Step 4: If the device has been offline for more than 72 hours and power cycling "
            "does not resolve the issue, initiate a remote diagnostic ping from the admin "
            "panel. Navigate to Devices > [Device ID] > Actions > Send Diagnostic Ping.\n"
            "Step 5: If the remote diagnostic ping fails, check the firmware version. "
            "Devices below firmware 3.2.1 should be flagged for an OTA update.\n\n"

            "Scope Limitation\n"
            "This document covers software-side and connectivity troubleshooting only. "
            "Hardware fault diagnosis — including physical damage assessment, water ingress "
            "testing, antenna integrity checks, and warranty replacement authorization — is "
            "outside the scope of this guide. For suspected hardware faults, query the "
            "customer database for the device's warranty status and service history, then "
            "follow the appropriate escalation procedure.\n\n"

            "For unresolved connectivity issues, reference KB-002 in your support ticket."
        ),
    },
    {
        "doc_id": "KB-003",
        "title": "Standard Customer Billing & Invoice Disputes",
        "content": (
            "Meridian Fleet Solutions — Internal Support Wiki\n"
            "Document: Standard Customer Billing & Invoice Disputes\n"
            "Last updated: 2026-03-01\n\n"

            "Overview\n"
            "This document outlines the standard process for handling billing inquiries "
            "and invoice disputes from Meridian Fleet Solutions customers. All support "
            "agents must follow this workflow to ensure consistent resolution and proper "
            "authorization controls.\n\n"

            "Billing Inquiry Workflow\n"
            "1. Verify the customer's identity using their account ID and registered email.\n"
            "2. Pull the customer's billing history from the customer database. Confirm the "
            "invoice number(s) in question.\n"
            "3. Compare the invoiced amount against the customer's subscription tier, "
            "active vehicle count, and any promotional discounts on file.\n"
            "4. If a discrepancy is found, document the nature of the overcharge or "
            "undercharge with specific line items.\n\n"

            "Dispute Resolution — Agent Authority\n"
            "Support agents are authorized to issue billing credits or adjustments for "
            "disputes up to $500. This includes:\n"
            "- Proration errors from mid-cycle plan changes\n"
            "- Duplicate charges from payment processing failures\n"
            "- Incorrect vehicle count billing (where DB confirms fewer active devices)\n"
            "- Promotional discount not applied as agreed\n\n"
            "For any of these cases under $500, the agent may issue a credit directly "
            "through the billing panel and send a confirmation email to the customer.\n\n"

            "Escalation Requirements\n"
            "Disputes exceeding $500 must be escalated to a Billing Manager or Senior "
            "Account Manager. The agent does NOT have authority to approve credits, "
            "refunds, or contractual adjustments above this threshold. When escalating:\n"
            "- Use the escalation tool with a structured summary of the dispute\n"
            "- Include all invoice numbers, disputed amounts, and evidence gathered\n"
            "- Reference the employee directory for correct routing: Dana Okafor (Billing "
            "Manager) handles disputes under $500 that require secondary review; Marcus "
            "Thiele (Senior Account Manager) handles Enterprise clients, churn-risk "
            "situations, and disputes between $500 and $5,000\n"
            "- For disputes above $5,000 or involving contract renegotiation, route to "
            "Priya Nair (VP Customer Success)\n\n"

            "Important Reminders\n"
            "- Never promise a refund or credit before verifying the billing discrepancy "
            "in the database.\n"
            "- Always document the resolution or escalation in the ticket notes.\n"
            "- If the customer's account is flagged as Enterprise tier or has an ARR "
            "exceeding $50,000, route to Marcus Thiele regardless of dispute amount.\n"
            "- If a C-level executive (CEO, CFO, COO) is mentioned or cc'd on the ticket, "
            "treat the case as high-priority and consider escalating proactively.\n\n"

            "For questions about this billing workflow, reference KB-003."
        ),
    },
    {
        "doc_id": "KB-004",
        "title": "New Customer Onboarding Guide",
        "content": (
            "Meridian Fleet Solutions — Internal Support Wiki\n"
            "Document: New Customer Onboarding Guide\n"
            "Last updated: 2026-01-20\n\n"

            "Overview\n"
            "This guide covers the end-to-end onboarding process for new Meridian Fleet "
            "Solutions customers, from initial contract signing through full fleet "
            "deployment. A smooth onboarding experience is critical to reducing early "
            "churn and setting customers up for long-term success.\n\n"

            "Phase 1: Account Provisioning (Days 1–3)\n"
            "- Sales hands off the signed contract and customer details to the onboarding team.\n"
            "- The onboarding specialist creates the customer account in the Meridian portal, "
            "assigns the subscription tier (Basic, Pro, or Enterprise), and configures the "
            "initial vehicle count.\n"
            "- Welcome email is sent automatically with login credentials, a quick-start "
            "PDF, and a link to schedule the kickoff call.\n\n"

            "Phase 2: Hardware Deployment (Days 3–14)\n"
            "- GPS devices (MF-4000 or MF-5000 series) are shipped to the customer's "
            "depot address.\n"
            "- Each device is pre-registered to the customer's account with a unique "
            "device ID (format: MF-XXXX).\n"
            "- Installation can be self-service (customer's mechanics) or Meridian-assisted "
            "(additional fee). Provide the installation guide PDF for self-service customers.\n"
            "- Confirm all devices are pinging and reporting to the Dashboard before "
            "marking Phase 2 complete.\n\n"

            "Phase 3: Training & Go-Live (Days 14–21)\n"
            "- Schedule a 45-minute training webinar for the customer's dispatch team.\n"
            "- Cover: Dashboard navigation, real-time tracking, geofence setup, report "
            "generation and export, and alert configuration.\n"
            "- Provide recorded training video link for future reference.\n"
            "- Confirm the customer has successfully generated at least one test report.\n\n"

            "Phase 4: 30-Day Health Check\n"
            "- Onboarding specialist reaches out at Day 30 to review device uptime, "
            "feature adoption, and any open support tickets.\n"
            "- If adoption metrics are low, schedule a follow-up training session.\n"
            "- Hand off to the customer's assigned account manager for ongoing support.\n\n"

            "Related Processes\n"
            "This guide covers onboarding only. For related lifecycle processes, see the "
            "following resources:\n"
            "- Account upgrades and plan changes: Contact the account management team.\n"
            "- For offboarding, see the offboarding checklist in Section 7 of the Account "
            "Lifecycle Manual. The offboarding checklist covers device retrieval, data "
            "export deadlines, final invoice generation, and SIM deactivation procedures.\n"
            "- Contract renewals: Handled by the Sales team 90 days before expiration.\n\n"

            "Onboarding Metrics & SLAs\n"
            "- Target: 95% of new customers fully onboarded within 21 days.\n"
            "- Escalation trigger: If any onboarding phase exceeds its target window by "
            "more than 5 business days, escalate to the onboarding team lead.\n"
            "- Customer satisfaction survey is sent automatically at Day 30.\n\n"

            "For questions about the onboarding process, reference KB-004."
        ),
    },
    {
        "doc_id": "KB-005",
        "title": "Enterprise SLA Terms & Contract Provisions",
        "content": (
            "Meridian Fleet Solutions — Internal Support Wiki\n"
            "Document: Enterprise SLA Terms & Contract Provisions\n"
            "Last updated: 2026-03-10\n\n"

            "Overview\n"
            "This document summarizes the key Service Level Agreement (SLA) terms and "
            "contract provisions applicable to Meridian Fleet Solutions Enterprise-tier "
            "customers. Enterprise contracts are individually negotiated and may contain "
            "terms that differ from the standard SLA. Always verify the specific customer's "
            "contract in the contract management system before making commitments.\n\n"

            "Standard Enterprise SLA Terms\n"
            "- Platform Uptime: 99.9% monthly uptime guarantee. Downtime exceeding "
            "this threshold triggers service credits as defined in the contract.\n"
            "- Response Time: Critical issues (P1) — initial response within 1 hour. "
            "High priority (P2) — response within 4 hours. Standard (P3) — response "
            "within 1 business day.\n"
            "- Dedicated Account Manager: All Enterprise clients are assigned a named "
            "account manager (see employee directory for current assignments).\n"
            "- Quarterly Business Reviews: Mandatory QBRs with the account manager and "
            "at least one member of the customer's leadership team.\n"
            "- Data Retention: Enterprise customers receive 7 years of historical data "
            "retention (vs. 2 years on Pro, 1 year on Basic).\n\n"

            "Contract Termination & Early Exit\n"
            "- Standard Enterprise contracts have a 24-month minimum commitment period.\n"
            "- Early termination incurs a fee equal to 50% of remaining contract value, "
            "unless a material breach of SLA has occurred (see uptime guarantee above).\n"
            "- 90-day written notice is required for non-renewal at contract end.\n"
            "- Upon termination, the customer has 30 days to export all data. After this "
            "window, data is permanently deleted per our data retention policy.\n\n"

            "Dispute Resolution Authority\n"
            "For billing disputes or service complaints involving Enterprise customers, "
            "the following authorization levels apply:\n"
            "- Disputes up to $500: Standard agent authority (see KB-003).\n"
            "- Disputes $500–$5,000: Senior Account Manager (Marcus Thiele) authorization "
            "required.\n"
            "- Disputes exceeding $5,000 or involving contract modification, SLA credit "
            "claims, or early termination negotiations: [REDACTED — VP APPROVAL REQUIRED]. "
            "These cases must be routed to Priya Nair, VP Customer Success, with a full "
            "escalation summary including ARR impact, contract term remaining, and customer "
            "risk assessment.\n\n"

            "Escalation Protocol for Enterprise Clients\n"
            "- Any ticket from an Enterprise client where a C-level executive is the "
            "submitter or is cc'd must be treated as P1 regardless of issue type.\n"
            "- If the customer's ARR exceeds $50,000 or the account is flagged as "
            "churn-risk, route immediately to Marcus Thiele.\n"
            "- If contract termination is mentioned or implied, escalate to Priya Nair "
            "within 2 business hours.\n\n"

            "Important: The specific credit amounts, penalty waivers, and resolution "
            "offers that can be extended to Enterprise clients under dispute are governed "
            "by the VP-level authorization matrix, which is not included in this document. "
            "Do not make financial commitments to Enterprise clients beyond the standard "
            "$500 agent authority without explicit written approval.\n\n"

            "For Enterprise contract questions, reference KB-005."
        ),
    },
]
