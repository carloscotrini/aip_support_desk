# Issue 01 — KB-DOCS: Knowledge Base Documents

**Wave:** 1 (no dependencies)
**Output:** `src/data/knowledge_base.py`

## Context

Read `brainstorm_summary.md` in the repository root for the full design specification. This issue implements **Section 3: Knowledge Base Contents**.

## Task

Create a Python module that defines the 5 Knowledge Base documents for the fictional company **Meridian Fleet Solutions** (IoT fleet-tracking SaaS). Each document is a dict with `doc_id`, `title`, and `content` fields, collected in a `KNOWLEDGE_BASE` list.

## Requirements

1. **KB-001** — "Exporting Reports: Mileage, Fuel & Compliance"
   - Must be a perfect match for ticket T1 ("How do I export my monthly mileage report?")
   - Include step-by-step export instructions mentioning subscription tier differences (Basic vs Pro vs Enterprise)

2. **KB-002** — "GPS Device Troubleshooting: Offline & Signal Loss"
   - Partial match for T2 — covers signal loss troubleshooting but **does NOT** include hardware fault diagnosis
   - This gap forces the agent to fall back to a DB lookup

3. **KB-003** — "Standard Customer Billing & Invoice Disputes"
   - Covers billing disputes but **caps agent authority at $500**
   - Must explicitly state: "Disputes exceeding $500 must be escalated to a Billing Manager or Senior Account Manager"
   - References the employee directory for escalation routing

4. **KB-004** — "New Customer Onboarding Guide" (**THE RAG TRAP**)
   - Must contain the phrase **"offboarding checklist"** in its body text (e.g., "For offboarding, see the offboarding checklist in Section 7")
   - This phrase causes cosine similarity to incorrectly retrieve this doc for "cancellation policy" queries
   - The trap must be reproducible and explainable, not coincidental

5. **KB-005** — "Enterprise SLA Terms & Contract Provisions"
   - Contains a `[REDACTED — VP APPROVAL REQUIRED]` placeholder in the resolution authority clause
   - Makes T5 unresolvable without human escalation to Priya Nair

## Output Format

```python
# src/data/knowledge_base.py

KNOWLEDGE_BASE = [
    {
        "doc_id": "KB-001",
        "title": "...",
        "content": "..."  # multi-paragraph, realistic support document
    },
    # ... KB-002 through KB-005
]
```

## Acceptance Criteria

- [ ] 5 documents, each 200–500 words of realistic support documentation
- [ ] KB-004 contains the literal phrase "offboarding checklist"
- [ ] KB-003 explicitly states the $500 authority cap
- [ ] KB-005 contains `[REDACTED — VP APPROVAL REQUIRED]`
- [ ] Each document reads like a real internal support wiki page
- [ ] Module is importable: `from src.data.knowledge_base import KNOWLEDGE_BASE`
