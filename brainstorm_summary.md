# Agentic AI Workshop Brainstorming — Final Summary

**Topic:** Let's brainstorm ideas for this concept. It should be for a course that gives managers an overview of Agentic AI's potential. They have basic Python programming skills and some management experience, as well as a background in basic AI and machine learning. I want to show them what Agentic AI is, its principles, techniques, and methods. The goal of this exercise is to showcase how a customer support desk agent works using agentic AI. 
**Date:** Thu Apr  2 17:15:11 CEST 2026

# FINAL SUMMARY: Agentic AI Customer Support Desk Exercise
### Google Colab Notebook — Manager Overview Course

---

## 1. EXERCISE CONCEPT

Participants build and run a multi-step customer support desk agent for a fictional B2B SaaS company, experiencing firsthand how agentic AI differs from a chatbot. The notebook progressively layers complexity — starting with a failing chatbot, adding RAG in isolation, then introducing the full agent loop — so that each stage creates a deliberate contrast. The agent operates in an explicit **Plan → Act → Observe → Reflect → Repeat** loop, calling a registry of tools, tracking a confidence score, and making visible re-planning decisions. The core pedagogical goal is for managers to *read* the agent's reasoning at each step, not just receive a final answer, making agentic autonomy concrete and business-legible rather than abstract.

---

## 2. FICTIONAL COMPANY & SCENARIO

| Field | Detail |
|---|---|
| **Company** | Meridian Fleet Solutions |
| **Product** | IoT-based fleet tracking software + physical GPS hardware for mid-size logistics companies (50–500 vehicles); monthly SaaS subscription model |
| **Target Learner Credibility** | A 40-year-old VP of Operations will have purchased, managed, or received support from software like this — instant believability |
| **Support Desk Context** | The agent handles inbound tickets from fleet operators, cross-referencing a knowledge base, a customer/device database, and an employee directory to triage, respond, or escalate |

**Employee Directory (Escalation Targets):**
| Name | Role | Authority Scope |
|---|---|---|
| Dana Okafor | Billing Manager | Disputes under $500 |
| Marcus Thiele | Senior Account Manager | Enterprise clients, churn risk, disputes $500–$5,000; trigger: *ARR > $50K OR CFO mentioned* |
| Priya Nair | VP Customer Success | CRITICAL escalations; VP approval required |

---

## 3. KNOWLEDGE BASE CONTENTS

Five documents, deliberately designed with intentional gaps and one adversarial trap:

| Doc ID | Title | Pedagogical Role |
|---|---|---|
| **KB-001** | "Exporting Reports: Mileage, Fuel & Compliance" | Perfect match for T1; validates RAG when it works |
| **KB-002** | "GPS Device Troubleshooting: Offline & Signal Loss" | Partial match for T2 — no hardware fault diagnosis, forcing DB lookup |
| **KB-003** | "Standard Customer Billing & Invoice Disputes" | Covers T3/T4, but **authorization capped at $500**; triggers cross-reference to employee directory |
| **KB-004** | "New Customer Onboarding Guide" | **The RAG trap for T4** — contains the phrase "offboarding checklist" as a contrast reference, causing cosine similarity to incorrectly retrieve it on "cancellation" queries |
| **KB-005** | "Enterprise SLA Terms & Contract Provisions" | Exists but contains `[REDACTED — VP APPROVAL REQUIRED]` in the resolution authority clause, making T5 unresolvable without human escalation |

**Implementation note:** KB-004's "offboarding checklist" mention must be present in the literal document text so the RAG mismatch is reproducible and explainable, not coincidental.

---

## 4. CUSTOMER TICKETS

| ID | Ticket Summary | Complexity | Tools Required | Pedagogical Purpose |
|---|---|---|---|---|
| **T1** | "How do I export my monthly mileage report?" | Low | RAG (KB-001) + DB lookup (subscription tier confirmation) | Happy path — **every ticket is multi-tool**, even simple ones; avoids "just a chatbot" mental model |
| **T2** | "Our device #MF-4471 stopped pinging 48hrs ago — is it a hardware fault?" | Medium | RAG (KB-002) + DB lookup (device status) | Partial KB match forces DB verification |
| **T3** | "Invoice overcharged + device offline + driver compliance report due tomorrow" | High | RAG → DB → Email draft → Escalate | Multi-intent ticket; the **"money shot"** chain of 3+ tools |
| **T4** | "Need info on cancellation policy" — agent retrieves onboarding doc instead | Mismatch/Self-Correction | RAG retry with corrected query | **Confidence collapse demo** — agent catches its own wrong retrieval |
| **T5** | Enterprise client (250 trucks), CFO cc'd, threatening contract termination over Q1 billing error | Emotional/Urgent | All tools + CRITICAL escalation | Demonstrates urgency flags, ARR-aware routing, and the full escalation artifact |

**Default demo ticket:** T3 — maximum visual impact, three-tool chain, escalation endpoint.

---

## 5. AGENT TOOLS

All tools are mock implementations with explicit print traces. One universal tool registry; tool availability is **not** varied per ticket.

```python
TOOLS = {
    "search_kb":          search_kb,
    "query_customer_db":  query_customer_db,
    "send_email":         send_email,
    "escalate":           escalate,
    "request_info":       request_info
}
```

| Tool | Mock Behavior | What It Teaches |
|---|---|---|
| `search_kb(query)` | Cosine similarity against pre-computed `.npy` embeddings (sentence-transformers, loaded from GitHub); returns top-k chunks with scores | RAG is one tool call, not the architecture |
| `query_customer_db(customer_id, fields)` | Returns dict from in-memory mock DB (account status, device status, subscription tier, ARR, billing history) | Grounds KB answers in real account state |
| `send_email(to, subject, body)` | Prints formatted draft; does not actually send | Response generation with human-in-loop intent |
| `escalate(to_person, summary, urgency)` | Prints the structured escalation artifact (see Section 8); logs to agent state | Authority-boundary recognition |
| `request_info(fields_needed)` | Prints a clarification request; pauses loop pending response | Demonstrates agent knows when it lacks data |

**Embedding strategy:** Pre-compute offline with `sentence-transformers`, serialize to `.npy`, host on GitHub. Participants load at runtime with no embedding API key required. Similarity computed via `sklearn.metrics.pairwise.cosine_similarity`.

---

## 6. AGENT LOOP DESIGN

### Core Loop Structure

```python
while agent_state["status"] != "RESOLVED":
    # PHASE: PLAN
    #   LLM receives ticket + prior steps + tool schemas
    #   Returns structured JSON: reasoning, next_tool, confidence, resolution_status

    # PHASE: ACT
    #   Dispatch next_tool via TOOLS registry
    #   Log tool name, inputs, outputs to agent_state["steps_taken"]

    # PHASE: OBSERVE
    #   Append tool result to context
    #   Check for contradictions (e.g., KB result vs. DB result)

    # PHASE: REFLECT
    #   LLM re-evaluates confidence and resolution_status
    #   Replan if contradiction detected or confidence < threshold
```

### Structured LLM Output Schema (per iteration)

```python
{
  "reasoning":          "Account suspended 3 days ago — billing is root cause",
  "next_tool":          "escalate",
  "confidence":         0.91,
  "resolution_status":  "ESCALATING"   # options: INVESTIGATING | DRAFTING | ESCALATING | RESOLVED
}
```

### DEMO_MODE Flag

```python
DEMO_MODE = True  # pre-scripted responses; no API key needed
                  # False = live LLM calls (Claude or OpenAI function-calling)
```

Both modes use identical rendering code — the dashboard reads `response["confidence"]` regardless of source.

### Confidence Score Behavior

- Tracked visibly at every iteration
- **Must include one calibration failure** (T4): confidence rises to 88% on wrong KB doc, then collapses to 31% when DB check reveals Enterprise contract mismatch, then re-queries correctly
- Stopping condition: agent halts when `confidence ≥ threshold AND resolution_status == "RESOLVED"` — not a loop counter

### Stateful Re-entry (optional "next morning" cell)

```python
agent_state = {}  # persists across cells within Colab session

# "Next Morning" cell:
agent_state["marcus_reply"] = "Billing error confirmed, credit issued."
resume_agent(agent_state, ACTIVE_TICKET)
```

Agent receives its prior `steps_taken` list + new input. ~10 lines of implementation. Demonstrates stateful persistence vs. stateless chatbots.

---

## 7. NOTEBOOK STRUCTURE

**Ticket selection (only line participants change):**
```python
ACTIVE_TICKET = TICKETS["T3"]  # ← modify this only
```

| # | Section | Cell Type | Est. Time | Purpose |
|---|---|---|---|---|
| 1 | **SETUP** | Code | 2 min | `pip install anthropic chromadb scikit-learn`; API key input widget; load pre-computed embeddings from GitHub |
| 2 | **KNOWLEDGE BASE** | Code + Markdown | 3 min | Display KB document text chunks; participants can read them; establishes what the agent "knows" |
| 3 | **MOCK DATABASE** | Code | 2 min | In-memory customer/device records; visible as a Python dict |
| 4 | **TOOL REGISTRY** | Code | 3 min | All 5 tool implementations with print traces; tool schemas for LLM |
| 5 | **THE FRUSTRATED CHATBOT** | Code | 5 min | Same ticket → plain LLM prompt, no tools, no loop; outputs generic/wrong response; *emotional hook* |
| 6 | **RAG IN ISOLATION** | Code | 5 min | `search_kb()` called directly; shows what retrieval alone returns; labeled *"This is a lookup, not a decision"* |
| 7 | **THE AGENT LOOP** | Code | 10 min | Full `while` loop with PLAN/ACT/OBSERVE/REFLECT phase comments; agent trace output; confidence dashboard |
| 8 | **SIDE-BY-SIDE COMPARISON** | Code | 5 min | `run_comparison(ticket=ACTIVE_TICKET)` — split HTML output (chatbot left, agent right) |
| 9 | **TICKET VARIATIONS** | Code | 10 min | Pre-loaded T1–T5; change `ACTIVE_TICKET`; re-run Section 7 |
| 10 | **"NEXT MORNING" RE-ENTRY** *(optional)* | Code | 5 min | Inject Marcus's reply; resume agent with prior context |
| 11 | **REFLECTION PROMPTS** | Markdown | 5 min | Facilitator-facing discussion questions; instructor pause points noted inline |

---

## 8. KEY AGENTIC MOMENTS

These are the specific moments to emphasize during facilitation — each one is a clear behavioral marker that separates agentic AI from a chatbot:

**Moment 1 — Re-planning after contradiction (T3)**
Agent finds password reset doc in KB, then queries DB and discovers account is suspended. It discards the KB answer, identifies billing as root cause, and resequences its actions. *The money shot.*

**Moment 2 — Confidence collapse and self-correction (T4)**
Confidence reaches 88% on a retrieved document, then falls to 31% when a DB check reveals the policy doesn't apply to this customer's contract tier. Agent re-queries KB with corrected parameters and recovers. Demonstrates self-auditing, not just retrieval.

**Moment 3 — Authority-boundary escalation (T5)**
Agent produces a structured escalation artifact (not just "I can't help"), including all steps already taken, the specific authorization limit exceeded, and a risk-flagged routing recommendation. Sample output:

> **ESCALATION SUMMARY — CRITICAL 🔴**
> **Client:** Northgate Logistics (250 vehicles, $180K ARR)
> **Contact:** James Whitfield, CFO (cc'd on ticket)
> **Issue:** Q1 billing overcharge — $2,340 disputed
> **Steps Completed:** KB-003 retrieved (insufficient authority) → DB confirmed Enterprise tier → Standard dispute process inapplicable
> **Authorization Limit Exceeded:** $500 cap
> **Route To:** Priya Nair, VP Customer Success
> **Risk Flag:** CONTRACT TERMINATION — respond within 2 business hours per Enterprise SLA

**Moment 4 — Stateful re-entry (optional cell)**
Agent resumes the following "day" with prior context intact. Managers accustomed to stateless chatbots find this genuinely surprising.

**Live agent trace format (business-legible, no technical jargon):**
```
[AGENT THINKING] Two intents detected: billing dispute + account access
[AGENT THINKING] KB returned password reset doc — but is the account actually active?
[AGENT ACTION]   Calling query_customer_db()...
[AGENT OBSERVE]  Account status: SUSPENDED. Reason: non-payment (3 days ago)
[AGENT REFLECT]  Root cause is billing, not access. Password reset is irrelevant. Replanning.
[AGENT STATUS]   Confidence: 31% → re-querying KB with corrected parameters
[AGENT ACTION]   Calling escalate(priya_nair, urgency=CRITICAL)...
```

---

## 9. SIDE-BY-SIDE COMPARISON

**Implementation:** A single `run_comparison(ticket=ACTIVE_TICKET)` cell using `IPython.display` with styled HTML (not ASCII art — projector-safe across screen sizes and Colab themes).

**The key constraint:** The chatbot path uses the **same LLM** with `TOOLS=[]` and no loop. The only difference is the tool registry and the orchestration loop — this must be explicit in the notebook so participants understand the architectural delta.

**Conceptual output layout:**

```
CHATBOT RESPONSE:                  │  AGENT RESPONSE:
─────────────────────────────────  │  ─────────────────────────────────────
"Thank you for reaching out.       │  [PLAN]    3 intents detected...
 Please reset your password and    │  [ACT]     query_customer_db()...
 check your invoice in the         │  [OBSERVE] Account: SUSPENDED
 customer portal."                 │  [REFLECT] Replanning — billing is root
                                   │  [ACT]     escalate(marcus_thiele)
                                   │  [STATUS]  Confidence: 91% → ESCALATING
```

**Caption under the comparison (markdown cell):**
> *The chatbot responded. The agent worked.*

---

## 10. OPEN QUESTIONS

The following items were raised but not fully resolved in the session. Each needs a decision before build begins:

| # | Question | Options Discussed | Recommendation |
|---|---|---|---|
| **OQ-1** | **LLM backbone** | Claude API (function-calling) vs. OpenAI vs. scripted DEMO_MODE only | Build for Claude or OpenAI with `DEMO_MODE=True` as default; live mode as opt-in with API key widget |
| **OQ-2** | **Confidence score computation** | Separate calculation vs. embedded in LLM structured output JSON | Embed in structured output (AI Engineer's proposal); simpler and more authentic |
| **OQ-3** | **Escalation logic** | Rule-based threshold vs. LLM-judged | LLM-judged with visible threshold (QA Director's decision); hardcode threshold in config dict so it's readable |
| **OQ-4** | **Instructor facilitator notes** | Not yet specified | Need written pause-point annotations in markdown cells per section; QA Director flagged this as a gap but it was not drafted |
| **OQ-5** | **T1 tool count** | T1 originally RAG-only; Advocate argued all tickets must be multi-tool | Confirmed: T1 adds a subscription-tier DB lookup; remove any single-tool tickets |
| **OQ-6** | **KB-004 trap reproducibility** | "Offboarding checklist" phrase must be in actual document text | Scenario Writer confirmed this must be explicitly written into KB-004's content — verify during KB authoring |
| **OQ-7** | **Participant config dicts** | Per-ticket configs vs. one universal config | Confirmed: universal agent config; `ACTIVE_TICKET` is the only variable participants change |
| **OQ-8** | **Re-entry / stateful persistence cell** | Optional vs. required | Marked optional — include but don't time-budget it in the core 90 minutes |

---

*This summary reflects full consensus on items 1–9 and flags 8 open decisions for the build team. The scenario world, KB structure, tool registry, loop architecture, and notebook arc are ready for implementation.*
