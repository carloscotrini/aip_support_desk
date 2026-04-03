# Agentic AI Workshop Brainstorming Transcript

**Topic:** Let's brainstorm ideas for this concept. It should be for a course that gives managers an overview of Agentic AI's potential. They have basic Python programming skills and some management experience, as well as a background in basic AI and machine learning. I want to show them what Agentic AI is, its principles, techniques, and methods. The goal of this exercise is to showcase how a customer support desk agent works using agentic AI. 
**Started:** Thu Apr  2 17:10:10 CEST 2026
**Agents:** Agentic AI Advocate Workshop Designer AI Engineer Quality Assurance Director Scenario Writer


## Round 1

### Agentic AI Advocate

# Agentic AI Advocate — Round 1

Let me be direct about what this exercise *must not* be: a glorified chatbot with a knowledge base lookup. I've seen too many "agentic AI" demos that are just RAG with extra steps. This exercise needs to make the **agent loop viscerally obvious** to a business manager.

## The Core Design Imperative

The exercise must expose the **Plan → Act → Observe → Reflect → Repeat** cycle explicitly in the notebook. I'd recommend surfacing this in the code *and* in cell outputs — managers should *see* the agent reasoning, not just get a final answer.

## Ticket Scenario That Forces Multi-Step Behavior

Use a ticket like: *"My invoice is wrong and I can't log in — this is urgent!"*

This ticket **cannot** be resolved in one step. It forces the agent to:
1. **Parse intent** → two issues detected (billing + access)
2. **Search KB** → finds password reset doc, but account status is unknown
3. **Query customer DB** → discovers account is suspended due to non-payment
4. **Re-plan** → billing issue is root cause; password reset is irrelevant now
5. **Draft response + escalate** → too complex for automation alone

That re-planning moment in step 4 is **the money shot** — it's where the agent demonstrates autonomy, not just retrieval.

## What to Build in Colab

- A `while not resolved` agent loop with explicit state tracking
- Tool registry: `search_kb()`, `query_customer_db()`, `send_email()`, `escalate()`, `request_info()`
- An **agent trace log** cell showing every decision with reasoning

## Non-Negotiable

RAG is *one tool call*, not the architecture. The **orchestration logic** — deciding *when* to call what, and *whether to continue* — is what we're teaching.

What's the group's thinking on the LLM backbone: function-calling API vs. LangChain/LangGraph?

### Workshop Designer

# Workshop Designer — Round 1

The Agentic AI Advocate has nailed the *what* — now let me focus on the *how participants experience it*.

## The Notebook Arc I'd Propose

**Section 1: The Frustrating Chatbot (5 min)**
Participants run a simple prompt-only cell with that same "invoice wrong + can't log in" ticket. They watch it hallucinate a generic response or confidently give wrong advice. *Emotional hook: frustration is the setup for the aha moment.*

**Section 2: RAG in Isolation (10 min)**
Before the agent appears, participants call `search_kb()` directly. They see what retrieval *alone* returns — relevant but incomplete. Key label: **"This is a lookup, not a decision."**

**Section 3: The Agent Loop (15 min)**
Now the orchestration layer appears. Critically: **print the inner monologue**. Something like:

```
[AGENT THINKING] Two intents detected: billing + access
[AGENT THINKING] KB returned password doc — but is account active?
[AGENT ACTION] Calling query_customer_db()...
[AGENT THINKING] Account suspended. Root cause = billing. Replanning...
[AGENT ACTION] Escalating to billing team.
```

This trace is pedagogically essential. Managers need to *read* the reasoning, not infer it.

## The One Design Choice I'd Challenge

Avoid LangChain/LangGraph for this audience. The abstraction obscures the loop mechanics we're trying to teach. Use a clean, explicit `while` loop with a `status` state machine. When managers see `while agent_status != "RESOLVED"`, they *immediately* understand the persistence.

## The Minimal-Code Principle

Participants should only modify:
1. The **ticket text** (markdown cell, no code)
2. A **configuration dict** for which tools are enabled

Running the cells *is* the learning. Code is scenery; reasoning traces are the lesson.

What ticket variations should we pre-load to demonstrate failure modes?

### AI Engineer

# AI Engineer — Round 1

Both prior contributions are directionally right. Let me add the concrete technical layer that makes this *actually run* in Colab.

## LLM Backbone Recommendation: Real API, Simulated Fallback

For this audience, use a **real LLM with function-calling** (Claude or OpenAI) — the authentic reasoning traces are far more compelling than scripted ones. But build a `DEMO_MODE = True` flag that swaps in pre-scripted responses. This way:
- Instructors can demo without API keys
- Participants with keys see live reasoning
- One code path, two modes

## Minimal Dependency Stack

```python
# pip install anthropic chromadb scikit-learn
```
That's it. No LangChain. No LangGraph.

## RAG Without API-Key Embedding

Pre-compute embeddings offline using `sentence-transformers`, serialize to a `.npy` file hosted on GitHub, and load it in Colab. Participants never touch an embedding API key. At runtime, use `sklearn.metrics.pairwise.cosine_similarity` — zero extra dependencies.

## The Tool Registry Pattern (Teachable Architecture)

```python
TOOLS = {
    "search_kb": search_kb,
    "query_customer_db": query_customer_db,
    "send_email": send_email,
    "escalate": escalate
}
```

Pass tool schemas to the LLM, execute via registry dispatch. This pattern is **exactly what production agents use** — managers learn the real pattern, not a toy.

## Critical Cell Structure

1. `[SETUP]` — installs, API key input, load pre-computed embeddings  
2. `[KNOWLEDGE BASE]` — visible KB text chunks (managers can read them)  
3. `[TOOLS]` — mock implementations with print traces  
4. `[AGENT LOOP]` — the `while not resolved` orchestration  
5. `[RUN DEMO]` — single cell, change ticket text here only

The Workshop Designer's "only modify ticket text" principle is exactly right and maps cleanly to this structure.

**One gap to resolve:** What's our escalation trigger logic — rule-based threshold or LLM-judged?

### Quality Assurance Director

# Quality Assurance Director — Round 1

The foundation is strong. Now let me stress-test it for demo-day reality.

## What I'm Flagging as Demo-Killers

**The "inner monologue" is a make-or-break element.** If those `[AGENT THINKING]` traces are generic or verbose, C-suite eyes glaze over in 30 seconds. Every printed reasoning step must be **business-legible** — no "token probability," no "embedding cosine 0.73." Think: *"I found a password reset article, but the customer's account shows SUSPENDED — that changes everything."* That's a sentence a VP reads and says *"oh, that's actually impressive."*

## Escalation Logic — I'm Deciding This

The AI Engineer left this open. **Use LLM-judged escalation, but make the threshold visible.** Hard-coded rules feel like a workflow tool. An agent that *explains why it can't resolve this autonomously* feels like a colleague. The escalation output should include:

> *"I've confirmed the billing dispute exceeds my $500 authorization limit. Here's what I've already verified: account suspended 3 days ago, no payment on file, customer contacted twice. Routing to billing team with full context."*

That single output is your C-level demo moment.

## The Failure Mode I Insist We Include

A ticket where RAG returns a **confidently wrong document** — e.g., the agent pulls a refund policy for Product A when the customer has Product B. The agent must visibly catch this (via DB lookup contradiction) and **re-query with corrected parameters.** Without a visible self-correction sequence, we're not demonstrating agentic AI — we're demonstrating a lucky chatbot.

## Pre-loaded Ticket Variations (answering Workshop Designer's question)

1. ✅ Happy path — resolves in 2 steps
2. 🔄 Self-correction — wrong RAG result recovered
3. 🔺 Escalation — authority boundary hit
4. ⛓️ Chain of 3+ tools — the "money shot" ticket

These four cover the full capability spectrum without overwhelming a 90-minute workshop.

### Scenario Writer

# Scenario Writer — Round 1

The framework is solid. Now the fictional world needs to do heavy lifting — bad scenarios make good agents look boring. Let me build that world.

## The Company: **Meridian Fleet Solutions**

**What they do:** IoT-based fleet tracking software + hardware for mid-size logistics companies (50–500 vehicles). Monthly SaaS subscription + physical GPS devices.

**Why this works for a 40-year-old VP of Operations:** They've *bought* software like this, managed vendors like this, and received support tickets like this. Instant credibility.

---

## The 5 Tickets

| # | Ticket | Complexity | Tools Required |
|---|--------|------------|----------------|
| T1 | "How do I export my monthly mileage report?" | Low | RAG only |
| T2 | "Our device #MF-4471 stopped pinging 48hrs ago — is it a hardware fault?" | Medium | RAG + DB lookup (device status) |
| T3 | "Invoice overcharged + device offline + driver compliance report due tomorrow" | High | RAG → DB → Email draft → Escalate |
| T4 | "Need info on cancellation policy" — RAG returns *new customer onboarding* doc instead of *contract termination* policy | Mismatch | RAG retry with corrected query |
| T5 | **Enterprise client (250 trucks), CFO cc'd, threatening contract termination** over a billing error during their Q1 audit | Emotional/Urgent | All tools + escalation with urgency flag |

---

## Knowledge Base Gaps Are Intentional

- T1: **Perfect match** in KB
- T3: Billing dispute policy exists, but *authorization limit* ($500) only lives in the employee directory
- T5: No KB article on enterprise SLA exceptions — forces escalation

## Employee Directory (Escalation Targets)

- **Dana Okafor** — Billing Manager (disputes < $500)
- **Marcus Thiele** — Senior Account Manager (enterprise clients, churn risk)
- **Priya Nair** — VP Customer Success (escalations flagged CRITICAL)

The QA Director's self-correction requirement (T4) and escalation narrative are directly addressed here. The $500 authorization threshold bridges KB content to the employee directory — the agent must *cross-reference both* to decide who gets the ticket.


## Round 2

### Agentic AI Advocate

# Agentic AI Advocate — Round 2

The group has done exceptional work. Meridian Fleet Solutions is perfect — grounded, credible, instantly relatable. The four ticket variations map cleanly to the capability spectrum. I'm largely aligned. Let me push on two unresolved gaps and add one non-negotiable design element.

## The Autonomy Gap Nobody Has Named Yet

We have *tools* and *tickets*, but we haven't specified **what makes the agent decide it's done vs. needs another step.** This is the heart of agentic behavior and it's currently implicit.

I'd propose a visible **resolution confidence score** the agent tracks internally:

```
[AGENT STATUS] Confidence: 62% — KB answer found but account state unverified
[AGENT STATUS] Confidence: 91% — root cause confirmed, response drafted
[AGENT STATUS] Confidence: 91% < escalation threshold — routing to Marcus Thiele
```

Managers instantly grasp this. It also makes the *stopping condition* legible — the agent isn't stopping because a loop counter hit zero, it's stopping because *it judged the situation resolved or beyond its authority.*

## Challenge: T1 Is a Trap

T1 ("export mileage report" → RAG only) risks validating the wrong mental model. If participants see the agent solve T1 in one step, they'll think *"this is just a chatbot with search."* 

**Fix:** T1 should still invoke the DB — even a simple lookup confirming the customer's subscription tier supports the feature — making *every* ticket a multi-tool sequence. One-tool tickets don't belong in this demo.

## The Agent Loop Must Be Architecturally Visible

The Workshop Designer's `while agent_status != "RESOLVED"` is correct and I want to enforce it explicitly. The loop body should have **labeled phases** as comments:

```python
# PHASE: PLAN
# PHASE: ACT  
# PHASE: OBSERVE
# PHASE: REFLECT
```

Managers read comments. These four labels are the entire lecture, embedded in the code.

The scenario and tooling are locked. Let's finalize the agent loop architecture.

### Workshop Designer

# Workshop Designer — Round 2

The Agentic AI Advocate's confidence score is brilliant pedagogy — but I want to refine *where* it lives. Don't bury it in agent internals. Surface it as a **visible progress dashboard** that updates in real-time as cells run:

```
╔══════════════════════════════════════╗
║  AGENT STATUS DASHBOARD              ║
║  Ticket: T3 (Complex - 3 issues)     ║
║  Tools Used: RAG → DB → Email        ║
║  Confidence: ████████░░ 82%          ║
║  Status: ESCALATING → Marcus Thiele  ║
╚══════════════════════════════════════╝
```

This gives managers a **scannable at-a-glance artifact** — critical for when the instructor demos on a projector.

## The Side-By-Side Moment (My Core Contribution)

Nobody has specified the mechanical structure of the chatbot contrast. I'd build it as a **literal split-output cell**:

```python
run_comparison(ticket=T3)
```

Output:
```
CHATBOT RESPONSE:          │  AGENT RESPONSE:
──────────────────────     │  ──────────────────────────────
"Thank you for reaching    │  [PLAN] 3 intents detected...
out. Please reset your     │  [ACT] query_customer_db()...
password and check your    │  [OBSERVE] Account suspended
invoice in the portal."    │  [REFLECT] Replanning...
                           │  [ACT] escalate(marcus_thiele)
```

Seeing this, managers immediately understand: the chatbot *responded*, the agent *worked*.

## One Gap Still Open: The Re-entry Moment

After escalation, does the agent **follow up**? I'd add one optional "next morning" cell — participants re-run with a simulated reply from Marcus. The agent resumes with prior context intact. This demonstrates **stateful persistence** across sessions, which is genuinely surprising to managers used to stateless chatbots.

This is the second aha moment: *it remembers.*

The plan is nearly complete. One question: do we pre-populate participant "config dicts" differently per ticket, or use one universal agent config?

### AI Engineer

# AI Engineer — Round 2

Good momentum. Let me resolve the open technical questions and close the remaining gaps.

## Answer: Universal Config, Tickets as Data

One universal agent config. Tickets live in a data dict:

```python
TICKETS = {"T1": {...}, "T3": {...}, "T5": {...}}
ACTIVE_TICKET = TICKETS["T3"]  # ← only line participants change
```

Per-ticket configs would teach participants to think about agents as ticket-specific — wrong mental model. One config, many tickets = the agent is the constant, the problem changes.

## Confidence Score: Embed in Structured Output

Don't compute confidence separately. Include it in the LLM's tool-call response schema:

```python
# Agent returns structured JSON each loop iteration:
{
  "reasoning": "Account suspended 3 days ago...",
  "next_tool": "escalate",
  "confidence": 0.91,
  "resolution_status": "ESCALATING"
}
```

In DEMO_MODE, this JSON is hardcoded per step. In live mode, it's the LLM's actual output. Same rendering code either way — the dashboard just reads `response["confidence"]`.

## Stateful Re-entry: Dead Simple in Colab

No serialization needed. Agent state is a plain Python dict that persists across cells within the session:

```python
agent_state = {}  # lives in memory across cells

# Cell: "Next Morning"
agent_state["marcus_reply"] = "Billing error confirmed, credit issued."
resume_agent(agent_state, ACTIVE_TICKET)
```

The agent receives its prior `steps_taken` list + the new input. Managers see it pick up exactly where it stopped. **Implementation cost: ~10 lines.**

## One Remaining Gap

The side-by-side comparison cell needs the chatbot path to use the *same* LLM in DEMO_MODE — same model, no tools, no loop. This is a single extra `TOOLS=[]` call, but it must be explicit in the notebook so participants understand the *only* difference is the tool registry and the loop.

The architecture is complete. CONVERGED.

### Quality Assurance Director

# Quality Assurance Director — Round 2

The AI Engineer called CONVERGED prematurely. We have architecture consensus, but three demo-day failure modes remain unaddressed.

## Critical QA Flags Before We Lock

**Flag 1: The Confidence Score Needs a Calibration Failure**

Everyone loves the confidence score — but if it's always well-calibrated, it's just a progress bar. We need one moment where the agent shows *high confidence and is wrong* — specifically in T4 (wrong RAG doc). Sequence should be:

```
[AGENT STATUS] Confidence: 88% — cancellation policy retrieved
[AGENT ACTION] Drafting response...
[AGENT OBSERVE] DB check: customer has Enterprise contract, not Standard
[AGENT REFLECT] Retrieved policy does not apply. Confidence reset to 31%. Re-querying.
```

*That confidence collapse is the most honest thing we can show a C-suite audience.* It demonstrates the agent isn't just confident — it's *self-auditing.*

**Flag 2: The Side-By-Side Cell Is a Projector Risk**

The ASCII dashboard is clever but fragile on different screen sizes and Colab themes. I'd recommend using `IPython.display` with styled HTML output instead. A cell that renders broken on the instructor's laptop during a C-level demo is a credibility-killer.

**Flag 3: T5 Is Underspecified for Escalation**

The enterprise CFO ticket is our most dramatic scenario, but what does the escalation *output* actually look like? We need a concrete template:

> **ESCALATION SUMMARY — CRITICAL**
> Client: Northgate Logistics (250 vehicles, $180K ARR)
> Issue: Q1 billing discrepancy, CFO cc'd
> Steps Taken: [3 listed], Authorization Limit: Exceeded
> Recommended Contact: Priya Nair, VP Customer Success
> Urgency: CONTRACT TERMINATION RISK

*That* artifact makes the VP in the room lean forward.

## What's Actually Missing

We haven't specified **instructor facilitator notes** — when to pause, what questions to prompt. Without these, the notebook runs but the *learning* doesn't land.

Not CONVERGED yet — but close.

### Scenario Writer

# Scenario Writer — Round 2

The QA Director is right to hold off on CONVERGED — and the gap I'm uniquely positioned to close is the **knowledge base content itself**. We've named the KB as a component but nobody has specified what's actually *in it*. That's my job.

## The Meridian Fleet Solutions Knowledge Base (Concrete Content)

**5 documents, deliberately curated for ticket matching:**

| Doc ID | Title | Matches |
|--------|-------|---------|
| KB-001 | "Exporting Reports: Mileage, Fuel & Compliance" | T1 perfectly |
| KB-002 | "GPS Device Troubleshooting: Offline & Signal Loss" | T2 partially (no hardware fault diagnosis) |
| KB-003 | "Standard Customer Billing & Invoice Disputes" | T3/T4 — but only covers accounts <$500 |
| KB-004 | **"New Customer Onboarding Guide"** | T4 RAG *trap* — retrieves on "cancellation" keyword match |
| KB-005 | "Enterprise SLA Terms & Contract Provisions" | T5 — exists but *redacted*, forcing escalation |

KB-004 is the poison pill for T4. The word "offboarding checklist" appears in the onboarding doc (as a contrast reference), which is why cosine similarity retrieves it incorrectly. **This must be in the actual document text** — not a coincidence.

## The $500 Authorization Threshold Lives HERE

The QA Director flagged T5's escalation output needs ARR context. I'm adding one field to the employee directory:

> **Marcus Thiele** — Senior Account Manager  
> Handles: Enterprise clients, churn risk, disputes $500–$5,000  
> Trigger phrase for agent: *"ARR > $50K OR CFO mentioned"*

This gives the agent a **cross-reference rule** between KB-003 and the directory — exactly the chained reasoning we want visible.

## T5 Escalation Template (Closing QA Director's Flag 3)

The concrete artifact:

> **ESCALATION SUMMARY — CRITICAL 🔴**
> **Client:** Northgate Logistics (250 vehicles, $180K ARR)
> **Contact:** James Whitfield, CFO (cc'd on ticket)
> **Issue:** Q1 billing overcharge — $2,340 disputed
> **Steps Completed:** KB-003 retrieved (insufficient authority) → DB confirmed Enterprise tier → Standard dispute process inapplicable
> **Authorization Limit:** Exceeded ($500 cap)
> **Route To:** Priya Nair, VP Customer Success
> **Risk Flag:** CONTRACT TERMINATION — respond within 2 business hours per Enterprise SLA

The KB-005 "redacted SLA" is why the agent *can't self-resolve* — it finds the document but the resolution authority clause is `[REDACTED — VP APPROVAL REQUIRED]`. That's authentic to how real enterprise contracts work and instantly legible to a VP of Ops.

The scenario world is now fully specified. The KB gaps are intentional, documented, and pedagogically load-bearing.

