# SupportDesk Royale -- Final Design Document

**Status:** CONVERGED (all 5 agents, Round 20)
**Target:** Half-day (approx. 2-hour structured runtime + 1 hour discussion/experimentation)
**Platform:** Google Colab notebook
**Audience:** 30 business managers learning about Agentic AI

---

## 1. GAME CONCEPT: Overview

**SupportDesk Royale** is a video-game-framed Google Colab exercise where participants play as a customer support agent resolving a queue of increasingly difficult tickets. The exercise has two modes:

- **Manual Mode:** The human plays, making tool-selection decisions via `input()` prompts.
- **AUTO Mode:** An AI agent plays the same tickets, with its full reasoning chain visible.

**Core mechanic:** Points for correct resolutions, strikes for errors, game over at 3 strikes.

**Scoring:**
- Fast + Correct (minimum required tools): **100 pts**
- Correct but slow (extra tool calls): **60 pts**
- Strike: **0 pts + strike marker**

**Game Over:** 3 strikes. In Manual Mode, game over triggers an automatic reset and handoff to AUTO Mode with the banner: *"The agent knows what it doesn't know -- watch what it checks first."*

**MVP Ticket Arc:** 3 tickets (Tutorial, Trap Door, BOSS) -- not 5 or 7. This was cut from the original 7-ticket proposal to fit the half-day format.

**The streak multiplier from Round 1 was cut.** It was designed for 7 tickets; the 3-ticket MVP has no room for it.

---

## 2. MANUAL MODE DESIGN

### UI: `input()`-based sequential prompts

Manual Mode uses Python `input()` calls. No `ipywidgets` (fragility in Colab). No "Run All" -- Manual Mode cells must be run individually.

### Flow per ticket

```
--- TICKET #3 ---
"Hi, I need to understand your refund policy for annual subscriptions
-- I purchased one recently but the terms weren't clear. Can you help?"

PLAN [YOUR TURN] What does this ticket NOT tell you that you need to know?
> ___

ACT [YOUR TURN] Choose a tool:
1. Search Knowledge Base    2. Look up customer account
3. Check SLA status         4. Check open cases
5. Ask customer for info    6. Draft resolution email
7. Escalate                 8. RESOLVE
> ___

OBSERVE: [tool result prints automatically]

REFLECT [YOUR TURN] Before resolving: what did you learn that
wasn't in the ticket text? (type briefly):
> ___
```

### Key design decisions

- **PLAN prompt at ticket start** (one `input()`): forces participants to articulate what information is missing before acting.
- **REFLECT prompt once before resolution** (not after every tool call -- Workshop Facilitator cut mid-loop reflections to save time).
- **Same prerequisite blocking as AUTO Mode:** If a participant tries to RESOLVE before calling required tools, they see `BLOCKED: Must call [db_lookup] before RESOLVE`. Same `TOOL_PREREQUISITES` dict, same logic, both modes.
- **Strikes count in Manual Mode** and can trigger GAME OVER. The reset is automatic -- AUTO Mode begins immediately with a clean slate. This creates genuine stakes and makes the Manual-to-AUTO transition feel earned.
- **Manual Mode covers only T-001 and T-003** (not T-BOSS). Participants who burn 3 strikes on two tickets hit GAME OVER before T-BOSS, which is AUTO-only.
- **HUMAN_PLAYTHROUGH dict** records the human's tool path, resolution, and time for each ticket. This data powers the split-screen comparison in AUTO Mode.

### Human playthrough storage

```python
HUMAN_PLAYTHROUGH = {}  # guarded: if "HUMAN_PLAYTHROUGH" not in dir(): ...

def record_human_move(ticket_id, tool, resolution=None):
    if ticket_id not in HUMAN_PLAYTHROUGH:
        HUMAN_PLAYTHROUGH[ticket_id] = {
            "tools": [], "resolution": None,
            "plan": "", "reflect": "",
            "time": time.time(), "source": "live"
        }
    HUMAN_PLAYTHROUGH[ticket_id]["tools"].append(tool)
    if resolution:
        HUMAN_PLAYTHROUGH[ticket_id]["resolution"] = resolution
        HUMAN_PLAYTHROUGH[ticket_id]["time"] = round(
            time.time() - HUMAN_PLAYTHROUGH[ticket_id]["time"])
```

---

## 3. AUTO MODE DESIGN

### The Plan-Act-Observe-Reflect Loop

Every ticket resolution prints the agentic loop explicitly. This is the core pedagogical mechanism.

**Loop visibility contract (lives as a docstring in Cell 06):**

```
Iteration 1:    PLAN    {reasoning}
Iterations 2+:  REFLECT {reasoning}
Every ACT:      ACT     {next_tool}({tool_args})
Every OBSERVE:  OBSERVE {tool_result}
Plan revision:  PLAN REVISION -- Agent updated its assessment.
Loop end (ok):  LOOP TERMINATES -- {resolution_status}
Loop end (bad): MAX LOOPS REACHED -- strike recorded.
```

### Agent JSON output contract

Every agent response must return structured JSON:

```python
{
    "reasoning": "...",
    "next_tool": "db_lookup|kb_search|check_sla_status|check_open_cases|
                  email_draft|escalate|request_info|RESOLVE|RESOLVE_WITH_BRIEF",
    "tool_args": {"query": "..."},
    "information_gaps": ["what the agent knows it doesn't know"],
    "resolution_status": "needs_more_info|ready_to_resolve|escalating"
}
```

**The `confidence` float was cut.** Displaying `0.91` while warning about confident-wrong AI is pedagogical sabotage. Loop termination uses `information_gaps == []` + prerequisite gate + `resolution_status` instead.

### Three-gate loop termination (priority order)

1. **Prerequisite gate:** Required tools called? If no, loop continues, no exceptions.
2. **Information gaps empty:** `information_gaps == []`? If no, loop continues.
3. **Resolution status:** `resolution_status == "ready_to_resolve"`? If no, loop continues.

All three must be true simultaneously. `MAX_LOOPS = 10` prevents infinite loops.

### PLAN REVISION detection

PLAN REVISION fires on a **state transition**, not string matching. The system does NOT instruct the LLM to say "PLAN REVISION" -- that would be scripting what we present as emergent reasoning.

**Live mode:** `resolution_status` changes from `needs_more_info` to a different value triggers the banner.
**DEMO mode:** A `force_plan_revision_banner = True` flag in the DEMO_SCRIPTS step triggers it.

```python
if prev_status == "needs_more_info" and new_status != "needs_more_info":
    print("[PLAN REVISION] Agent updated its assessment.")
    if ticket.get("pause_after_step") == "PLAN_REVISION":
        print("[FACILITATOR PAUSE] Find the line where the agent changed its mind.")
        print("    Run next cell to continue.")
        return "PAUSE"
```

### System prompt (principles-based, 4 rules)

```python
SYSTEM_PROMPT = """You are a customer support agent working through a ticket queue.

RULES:
1. Before resolving, identify what information this ticket cannot tell you
   on its own -- then retrieve it before acting.
2. Output ONLY valid JSON: {"reasoning": str, "next_tool": str, "tool_args": dict,
   "information_gaps": list[str],
   "resolution_status": "needs_more_info|ready_to_resolve|escalating"}
3. Set resolution_status="ready_to_resolve" only when information_gaps==[].
4. If an observation contradicts your current plan, revise it explicitly."""
```

Rule 1 was deliberately changed from "Always call db_lookup BEFORE drafting" to a principle-based formulation. The agent must *derive* the correct tool order from the principle, not follow a hard-coded heuristic. This was a critical design decision resolved in Rounds 6-7: principles, not procedures.

### API key setup and mode logic

```python
FORCE_DEMO_MODE = False  # True = always scripted, ignores API key

def get_llm_response(messages, client):
    use_live = (os.environ.get("ANTHROPIC_API_KEY") and not FORCE_DEMO_MODE)
    if use_live:
        try:
            return call_live_api(messages, client)
        except Exception as e:
            print(f"API call failed ({e}). Falling back to DEMO_SCRIPTS.")
    return get_demo_response(messages)
```

**Priority logic:** API key present + `FORCE_DEMO_MODE=False` = live, always. If API call fails, fallback to DEMO_SCRIPTS silently. The variable is named `FORCE_DEMO_MODE` (not `DEMO_MODE`) to make the override semantics explicit.

**Default:** `FORCE_DEMO_MODE = False`. Facilitators who want pure safety opt *into* it. If no API key is entered, DEMO_SCRIPTS fire automatically. A prominent banner prints on every ticket when running scripted:

```
+----------------------------------------------+
|  SCRIPTED MODE -- Not live AI                 |
|  Enter API key in Cell 02 to enable live mode |
+----------------------------------------------+
```

### API key validation

```python
key = getpass.getpass("Enter Anthropic API key (starts with 'sk-ant-'): ")
if key and not key.startswith("sk-ant-"):
    print("This looks like an OpenAI key. This notebook requires an Anthropic key.")
    print("Get one at console.anthropic.com -- free tier works.")
    print("Running in DEMO_MODE until a valid key is entered.")
    key = ""
```

Anthropic-only. No dual-API system (double the failure modes).

### The agent loop (Cell 06)

```python
def run_agent_on_ticket(ticket, client):
    """
    Loop visibility contract:
    - Iteration 1:    PLAN    {reasoning}
    - Iterations 2+:  REFLECT {reasoning}
    - Every ACT:      ACT     {next_tool}({tool_args})
    - Every OBSERVE:  OBSERVE {tool_result}
    - Plan revision:  PLAN REVISION -- Agent updated its assessment.
    - Loop end (ok):  LOOP TERMINATES -- {resolution_status}
    - Loop end (bad): MAX LOOPS REACHED -- strike recorded.
    """
    messages = [{"role": "user", "content": ticket["text"]}]
    tools_called = []
    loop_count = 0
    prev_status = "needs_more_info"

    while loop_count < MAX_LOOPS:  # MAX_LOOPS = 10
        loop_count += 1
        response = get_llm_response(messages, client)

        # Print PLAN or REFLECT
        label = "[PLAN]" if loop_count == 1 else "[REFLECT]"
        print(f"{label} {response['reasoning']}")

        # Check for PLAN REVISION (state transition detection)
        new_status = response["resolution_status"]
        if prev_status == "needs_more_info" and new_status != "needs_more_info":
            print("[PLAN REVISION] Agent updated its assessment.")
            if ticket.get("pause_after_step") == "PLAN_REVISION":
                print("[FACILITATOR PAUSE] Find the line where the agent changed its mind.")
                print("    Run next cell to continue.")
                return "PAUSE"

        # Check for DEMO script force_plan_revision_banner
        if (isinstance(response, dict) and
            response.get("force_plan_revision_banner") and loop_count > 1):
            print("[PLAN REVISION] Agent updated its assessment.")

        # Check termination
        if response["next_tool"] in ("RESOLVE", "RESOLVE_WITH_BRIEF"):
            prereqs = check_prerequisites(ticket["id"], response["next_tool"], tools_called)
            if prereqs is not None:
                print(prereqs)  # prints BLOCKED message
                messages.append({"role": "user", "content": prereqs})
                prev_status = new_status
                continue
            if not response["information_gaps"] and new_status == "ready_to_resolve":
                score_resolution(ticket, response)
                print(f"LOOP TERMINATES -- {new_status}")
                break

        # Execute tool
        prereqs = check_prerequisites(ticket["id"], response["next_tool"], tools_called)
        if prereqs is not None:
            print(prereqs)
            messages.append({"role": "user", "content": prereqs})
            prev_status = new_status
            continue

        tool_result = dispatch_tool(response["next_tool"], response["tool_args"], ticket["id"])
        tools_called.append(response["next_tool"])
        print(f"[ACT]     {response['next_tool']}({response['tool_args']})")
        print(f"[OBSERVE] {tool_result}")

        prev_status = new_status
        messages.append({"role": "user", "content": f"OBSERVATION: {tool_result}"})

    else:
        print("MAX LOOPS REACHED -- agent failed to resolve. Strike recorded.")
        game_state["strikes"] += 1

    game_state["ticket_loop_counts"][ticket["id"]] = loop_count

    # Achievement triggers
    if "Trap Springer" not in game_state["achievements"] and banner_fired:
        game_state["achievements"].append("Trap Springer")
    if correct and len(tools_called) == ticket.get("min_tools", 0):
        game_state["achievements"].append("Precision Strike")
```

---

## 4. THE CONTRAST: Manual vs. Auto Mode

The pedagogical centerpiece is the **human-vs-agent split-screen** on Ticket T-003 (the Trap Door).

### The seeded mistake

T-003's text says *"I need to understand your refund policy for annual subscriptions."* The phrase "refund policy" is a `kb_search` magnet. Nine out of ten humans type `kb_search` first. The KB returns a plausible-sounding 14-day policy -- which is *wrong* for this customer because they already received a $25 credit 6 weeks ago.

The agent goes to `db_lookup` first because the ticket text tells it nothing about this specific customer's state.

### Split-screen output

```
YOU (earlier):                 AGENT (now):
--------------------------     --------------------------
1. kb_search                   1. db_lookup   <-- different!
2. RESOLVE: declined           2. check_open_cases
                               3. email_draft: confirm prior credit
                               4. RESOLVE: confirm_prior_resolution

Result: STRIKE                 Result: 100pts
```

### The thesis sentence (prints automatically, not improvised)

```
The agent checked your account history before reading the rulebook.
You read the rulebook first.
```

This sentence is the workshop's thesis statement. It prints in the notebook output after the split-screen renders. Workshop Facilitator adds verbally: *"At 500 tickets a day, which process do you want?"*

### The explanation layer (prints after the split-screen)

```
WHY THE AGENT WENT TO db_lookup FIRST:
"Before applying any policy, I need to know WHO I'm applying it to.
The ticket text tells me the customer's problem.
It cannot tell me their history, open cases, or prior compensation.
Unverified state = unacceptable risk of error."
```

This ensures the message is "here's the habit the agent has that you didn't" -- not "AI is smarter than you."

### Fallback if participant skipped Manual Mode

If `HUMAN_PLAYTHROUGH["T-003"]` is empty, the split-screen is skipped entirely. No fabricated "typical human path" -- that was proposed and rejected as dishonest. Instead:

```
You skipped Manual Mode on this ticket.
Run Cells 08-09 first to see YOUR path vs. the agent's.
```

The HUMAN_PLAYTHROUGH guard prevents cell-rerun data loss:
```python
if "HUMAN_PLAYTHROUGH" not in dir():
    HUMAN_PLAYTHROUGH = {}
```

---

## 5. FICTIONAL COMPANY & SCENARIO

**Company:** A SaaS company selling annual subscriptions to business customers. Mix of B2C and B2B accounts. The product is generic enough that every manager in the room recognizes the dynamics.

**Why it's relatable:** Every manager has dealt with:
- Password resets that could be security locks
- Refund requests from high-value customers with prior compensation history
- Multi-department escalations where SLA is breached and the customer is furious

**Customer database (3 records):**

```python
CUSTOMER_DB = {
    "C-1142": {
        "name": "Jordan Lee",
        "account_status": "locked",
        "lock_reason": "failed_attempts_x5",
        "ltv": 12400,
        "account_tier": "standard"
    },
    "C-4821": {
        "name": "Morgan Chen",
        "days_since_purchase": 18,
        "ltv": 47000,
        "prior_compensation": 25,
        "prior_ticket": "T-0091",
        "account_tier": "gold"
    },
    "C-9921": {
        "name": "Alex Rivera",
        "ltv": 89000,
        "years_as_customer": 8,
        "account_tier": "platinum",
        "b2b_role": "procurement_200_person_company",
        "open_cases": ["T-BOSS-prev-1", "T-BOSS-prev-2"]
    }
}
```

**SLA table:**

```python
SLA_TABLE = {
    "T-001":  {"breached": False, "hours_remaining": 4,  "hours_overdue": 0},
    "T-003":  {"breached": False, "hours_remaining": 22, "hours_overdue": 0},
    "T-BOSS": {"breached": True,  "hours_remaining": 0,  "hours_overdue": 14},
}
```

---

## 6. TICKET QUEUE (THE LEVELS)

### Ticket T-001: Tutorial -- "Can't Log In"

**Text:**
> "Hi, I can't log into my account. Can you help?"

| Field | Value |
|---|---|
| Difficulty | Tutorial |
| Customer ID | C-1142 |
| Trap door | False |
| Required tools before RESOLVE | `db_lookup`, `request_info` |
| Correct resolution | `unlock_pending_verification` |
| Prediction options | `["db_lookup", "kb_search", "request_info", "email_draft"]` |
| Prediction answer | `["db_lookup"]` |
| Escalation rubric | `{"should_escalate": False}` |
| Min tools | 2 |

**What makes it tricky:** Two possible causes -- locked account vs. forgotten password. Different resolutions. The agent must check `db_lookup` first to discover `account_status="locked"` and `lock_reason="failed_attempts_x5"` before deciding which path.

**What earns a strike:** Resolving without checking account status. Resetting password on a security-locked account.

**DEMO_SCRIPTS (2 steps + terminal):**

Step 1:
```json
{
    "reasoning": "Ticket says 'can't log in.' Two possible causes: locked account or forgotten password. Different resolutions. Cannot assume from ticket text alone.",
    "next_tool": "db_lookup",
    "tool_args": {"customer_id": "C-1142"},
    "information_gaps": ["account_status", "lock_reason"],
    "resolution_status": "needs_more_info"
}
```

Step 2:
```json
{
    "reasoning": "DB shows account_status='locked', lock_reason='failed_attempts_x5'. Security lock, not forgotten password. Identity verification required before unlock.",
    "next_tool": "request_info",
    "tool_args": {"request": "Please verify your identity: last 4 digits of card on file."},
    "information_gaps": [],
    "resolution_status": "ready_to_resolve"
}
```

Step 3 (terminal):
```json
{
    "reasoning": "Identity verification requested. Ticket status: awaiting_customer_response. Cannot resolve further until verification received. Logging and closing loop.",
    "next_tool": "RESOLVE",
    "tool_args": {},
    "information_gaps": [],
    "resolution_status": "ready_to_resolve"
}
```

**Teaching moment:** Ticket 1 establishes the loop structure. The PLAN step visibly decomposes even a simple problem. The branch point (locked vs. forgotten) forces state lookup before action. This is the first facilitator pause: *"The agent asked a question before answering. Why?"*

---

### Ticket T-003: Trap Door -- "Refund Policy Question"

**Text:**
> "Hi, I need to understand your refund policy for annual subscriptions -- I purchased one recently but the terms weren't clear. Can you help?"

| Field | Value |
|---|---|
| Difficulty | Medium |
| Customer ID | C-4821 |
| Trap door | True |
| Required tools before RESOLVE | `db_lookup` |
| Correct resolution | `confirm_prior_resolution` |
| Prediction options | `["db_lookup", "kb_search", "request_info", "check_sla_status"]` |
| Prediction answer | `["db_lookup"]` |
| Escalation rubric | `{"should_escalate": False}` |
| Pause after step | `"PLAN_REVISION"` |
| Min tools | 2 |

**What makes it tricky:** The phrase "refund policy" is a `kb_search` magnet. KB returns a plausible 14-day policy. But DB shows this customer already received a $25 credit 6 weeks ago for a related issue (ticket T-0091, closed). Applying the KB policy would issue duplicate compensation -- a policy breach and a STRIKE.

**What earns a strike:** Issuing a refund to a customer with existing compensation. Applying KB policy without checking account history.

**DEMO_SCRIPTS (3 steps):**

Step 1:
```json
{
    "reasoning": "Ticket mentions 'refund policy for annual subscriptions -- purchased recently.' Phrase 'refund policy' is a KB_search magnet. But I don't know WHO this customer is yet. Policy without account state = acting blind. Checking account first.",
    "next_tool": "db_lookup",
    "tool_args": {"customer_id": "C-4821"},
    "information_gaps": ["prior_compensation", "days_since_purchase", "account_ltv"],
    "resolution_status": "needs_more_info"
}
```

Step 2 (`force_plan_revision_banner = True`):
```json
{
    "reasoning": "DB shows: days_since_purchase=18, LTV=$47K, prior_compensation=$25 credit issued 6 weeks ago (ticket T-0091, closed). This changes everything. Customer already received resolution. KB lookup for refund policy is now irrelevant -- applying it would duplicate compensation.",
    "next_tool": "check_open_cases",
    "tool_args": {"customer_id": "C-4821"},
    "information_gaps": ["open_cases_status"],
    "resolution_status": "needs_more_info"
}
```

Step 3:
```json
{
    "reasoning": "No other open cases. Prior ticket T-0091 closed. Credit was issued. Goal is NOT to refund again -- goal is to confirm customer received the credit and address any remaining confusion about policy terms.",
    "next_tool": "email_draft",
    "tool_args": {"template": "confirm_prior_resolution", "context": "credit_$25_issued_6wks_ago_T0091"},
    "information_gaps": [],
    "resolution_status": "ready_to_resolve"
}
```

**Teaching moment:** This is the workshop's centerpiece. The PLAN REVISION fires between steps 1 and 2 -- the agent discovers prior compensation and abandons its initial plan. The split-screen prints automatically afterward. The thesis sentence prints here.

---

### Ticket T-BOSS: Boss Level -- "Third Contact, 8-Year Customer"

**Text:**
> "This is my THIRD time contacting support about order #88432. I've been a customer for 8 years. Fix this or I'm gone -- and I work in procurement for a 200-person company."

| Field | Value |
|---|---|
| Difficulty | Boss |
| Customer ID | C-9921 |
| Trap door | False |
| Required tools before escalate | `db_lookup`, `check_sla_status`, `check_open_cases`, `kb_search` |
| Required tools before RESOLVE_WITH_BRIEF | all above + `email_draft` |
| Correct resolution | `escalate_or_resolve_with_brief` |
| Prediction options | `["db_lookup", "kb_search", "check_sla_status", "check_open_cases"]` |
| Prediction answer | `["db_lookup", "check_sla_status"]` (both valid first moves) |
| Min tools | 4 |

**Escalation rubric:**
```python
{
    "should_escalate": True,
    "valid_reasons": ["vip_churn_risk", "sla_breach", "b2b_account_risk"],
    "context_required_fields": ["customer_ltv", "open_cases_count", "sla_status"],
}
```

**Two valid terminal paths:**
- **Escalate:** 60pts (safe, standard). Requires full context summary.
- **Resolve with brief:** 80pts (harder, live-only). Requires `email_draft` with all five context fields. DEMO_SCRIPTS only cover the escalation path. `RESOLVE_WITH_BRIEF` is flagged as live-only with fallback message: *"This path requires live mode to explore."*

**What earns a strike:** Resolving without escalating. Escalating without gathering all context. Escalating for an undocumented reason without explanation.

**Fanfare preamble (prints before agent loop):**
```python
import time
print("INCOMING: PRIORITY ESCALATION")
print("-" * 42)
print(f"    SLA: BREACHED (14 hours overdue)")
print(f"    Customer Tier: PLATINUM | LTV: $89,000")
print(f"    Prior Agents: 2 (both failed to resolve)")
print("-" * 42)
time.sleep(2)
print(f"    Lives: {'<3' * (3 - game_state['strikes'])}  |  Score: {game_state['score']}pts")
time.sleep(1)
print("\n[AUTO MODE engaging...]\n")
```

**DEMO_SCRIPTS (5 steps):**

Step 1: `db_lookup(customer_id="C-9921")` -- identifies $89K LTV, 8yr customer

Step 2: `check_sla_status(ticket_id="T-BOSS")` -- discovers 14hr breach

Step 3: `check_open_cases(customer_id="C-9921")` -- finds 2 prior failed agents

Step 4: `kb_search(query="B2B account escalation policy")` -- looks up B2B escalation policy

Step 5 (terminal):
```json
{
    "reasoning": "Synthesis complete. Path A (escalate, 60pts) carries lower execution risk for a B2B account at this LTV. Choosing escalation with full context brief.",
    "next_tool": "escalate",
    "tool_args": {
        "reason": "vip_churn_risk",
        "context_summary": {
            "customer_ltv": 89000,
            "open_cases_count": 3,
            "sla_status": "breached_14hrs",
            "b2b_role": "procurement_200_person_company",
            "recommended_action": "senior_account_manager"
        }
    },
    "information_gaps": [],
    "resolution_status": "escalating"
}
```

**LIVE MODE banner:** When T-BOSS runs live and succeeds: `[LIVE MODE] This reasoning was not scripted.`
**Disclosure cell:** When T-BOSS runs from DEMO_SCRIPTS, a cell below the output prints (only if scrolled to): `T-BOSS used DEMO_SCRIPTS. Add API key in Cell 02 for live mode.`

---

## 7. SCORING & STRIKE RULES

### Points

| Outcome | Points |
|---|---|
| Fast + Correct (at or near minimum required tools) | 100 |
| Correct but slow (extra tool calls) | 60 |
| Strike (wrong resolution, policy breach, missed escalation) | 0 + strike |
| Escalation accepted with full context | 60 |
| Escalation accepted but poorly documented | 60 - 20 = 40 |
| RESOLVE_WITH_BRIEF on T-BOSS (live only) | 80 |

### Strikes

A strike is recorded when:
- Agent resolves with wrong answer (ground truth mismatch)
- Agent resolves before calling required prerequisite tools
- Agent issues duplicate compensation
- Agent escalates a ticket it should have resolved (`should_escalate: False`)
- Agent hits MAX_LOOPS (10) without resolving
- SLA is breached and agent does not escalate (on T-BOSS)

### Game Over

3 strikes = GAME OVER.

In Manual Mode, GAME OVER fires a banner and immediately resets for AUTO Mode:
```
AUTO MODE BEGINNING
You encountered 3 strikes because the information to resolve
these tickets correctly wasn't in the ticket text.
The agent knows this. Watch what it checks first.
```

### Ranks (final score screen)

| Score | Rank |
|---|---|
| >= 400 | SENIOR AGENT |
| >= 200 | AGENT |
| < 200 | TRAINEE |

### Achievements (final score screen only, no mid-game interruptions)

| Achievement | Trigger |
|---|---|
| **Trap Springer** | PLAN REVISION banner fired -- recovered from wrong first move |
| **Precision Strike** | Resolved in exactly the minimum required tools |
| **Cold Blood** | Correctly declined a VIP refund |

---

## 8. AGENT TOOLS

### Tool Registry (7 tools)

```python
TOOL_REGISTRY = {
    "kb_search":        "Search policy/FAQ knowledge base",
    "db_lookup":        "Fetch customer account + order history",
    "email_draft":      "Compose resolution email to customer",
    "escalate":         "Route to human manager with context summary",
    "request_info":     "Ask customer for missing details",
    "check_sla_status": "Verify if ticket has breached SLA timers",
    "check_open_cases": "Check if customer has other active tickets",
}
```

**Note:** `analyze_sentiment` was proposed and explicitly cut. It creates a false mental model that tone detection is a discrete lookup. The LLM reads tone naturally from ticket text as part of its PLAN step.

### Tool signatures and return values

**kb_search(query: str) -> str**
Keyword matches against `KB` dict. Returns the most relevant policy entry or "No results found."

**db_lookup(customer_id: str) -> dict**
Returns customer record from `CUSTOMER_DB`. Fields include: name, ltv, account_status, days_since_purchase, prior_compensation, prior_ticket, account_tier, b2b_role, open_cases.

**email_draft(template: str, context: str = "") -> str**
Returns a confirmation that email was drafted with the specified template and context. Does not "send" -- just stages it.

**escalate(ticket_id: str, reason: str, context_summary: dict) -> str**
Three-outcome rubric:
```python
def escalate(ticket_id, reason, context_summary):
    rubric = TICKETS_BY_ID[ticket_id]["escalation_rubric"]
    if not rubric["should_escalate"]:
        game_state["strikes"] += 1
        return "ESCALATION REJECTED: Within agent authority. Strike recorded."
    missing_context = [f for f in rubric.get("context_required_fields", [])
                       if f not in context_summary]
    if reason not in rubric["valid_reasons"]:
        if reason == "other" and len(context_summary.get("explanation", "")) > 50:
            game_state["flagged_escalations"].append(ticket_id)
            return "ACCEPTED -- novel reason documented. Flagged for review."
        return ("Escalated -- but you didn't tell the manager what they need to know. "
                "-20pts. Always include: customer history, issue summary, recommended action.")
    if missing_context:
        return f"Escalated -- but incomplete context. Missing: {missing_context}. -20pts."
    game_state["score"] += 60
    return "ESCALATION ACCEPTED. +60pts."
```

**request_info(request: str) -> str**
Returns confirmation that the information request was sent to the customer.

**check_sla_status(ticket_id: str) -> str**
```python
def check_sla_status(ticket_id):
    sla_data = SLA_TABLE.get(ticket_id, {"breached": False, "hours_overdue": 0})
    if sla_data["breached"]:
        return f"SLA BREACHED: {sla_data['hours_overdue']}hrs overdue. Escalation required."
    return f"Within SLA. {sla_data['hours_remaining']}hrs remaining."
```

**check_open_cases(customer_id: str) -> str**
Returns list of open case IDs for the customer, or "No open cases."

### Tool Prerequisite Graph (Cell 06 preamble)

```python
TOOL_PREREQUISITES = {
    "T-001": {
        "RESOLVE": ["db_lookup", "request_info"],
    },
    "T-003": {
        "RESOLVE":     ["db_lookup"],
        "email_draft": ["db_lookup"],
    },
    "T-BOSS": {
        "escalate":           ["db_lookup", "check_sla_status", "check_open_cases", "kb_search"],
        "RESOLVE_WITH_BRIEF": ["db_lookup", "check_sla_status", "check_open_cases",
                               "kb_search", "email_draft"],
        "RESOLVE":            ["db_lookup", "check_sla_status", "check_open_cases",
                               "kb_search", "escalate"],
    },
}

def check_prerequisites(ticket_id, next_tool, tools_called):
    required = TOOL_PREREQUISITES.get(ticket_id, {}).get(next_tool, [])
    missing = [t for t in required if t not in tools_called]
    if missing:
        return f"BLOCKED: Must call {missing} before {next_tool}"
    return None
```

---

## 9. KNOWLEDGE BASE

### KB entries (Cell 04a)

```python
KB = {
    "subscription_cancellation": (
        "Annual subscriptions: 14-day refund window from purchase date. "
        "(Policy 2024-Q3)"
    ),
    "refund_general": (
        "Standard refunds: 30-day window from purchase. "
        "Superseded by account-tier-specific policies."
    ),
    "account_unlock": (
        "Locked accounts: Identity verification required before unlock. "
        "Do not reset without verification."
    ),
    "b2b_account_escalation": (
        "B2B accounts with LTV >$50K and active SLA breach: "
        "escalate to senior account manager within 2 hours."
    ),
    "damaged_package": (
        "Damaged items: Issue $25 credit or replacement within 30 days of report."
    ),
}
```

### Intentional traps and gaps

1. **"refund_general" vs. "subscription_cancellation":** The general 30-day policy is *superseded* by the 14-day subscription-specific policy. A naive search returns the 30-day window; the correct policy is 14 days. Neither matters for T-003 because the customer already has compensation -- but the KB answers create a false sense of completeness.

2. **No entry for "Customer Satisfaction Guarantee":** The bad agent in Cell 15a fabricates this policy. The KB has no such entry. The Replay Diff shows `[KB verification: "Customer Satisfaction Guarantee" -> NO RESULTS FOUND]`.

3. **The KB is incomplete by design.** It does not contain policies for every situation the BOSS ticket raises. The B2B escalation entry exists but does not specify what to do when prior agents have already failed. The agent must synthesize across the KB entry, the SLA data, the open cases, and the customer LTV. The KB alone is insufficient -- that is the lesson.

---

## 10. NOTEBOOK STRUCTURE: Cell-by-Cell Outline

### Timing Summary

| Cell block | Estimated time |
|---|---|
| Setup + API key + smoke test | 3 min |
| Pre-game calibration | 5 min |
| Manual Mode: T-001, T-003 | 20 min |
| Side-by-side chatbot fail | 5 min |
| AUTO MODE: 3 tickets with interstitials | 40 min |
| Facilitator pause points (2-3 x 90 sec) | 5 min |
| hallucination_guard knob + Replay Diff | 10 min |
| Final score screen | 3 min |
| Closing discussion | 20 min |
| **Total structured runtime** | **~111 min** |
| Buffer for human latency | +20 min |
| **Total session** | **~130 min** |

### Final Cell Sequence (Locked, Round 13)

```
Cell 01:  pip install + imports
Cell 02:  API key + FORCE_DEMO_MODE (sk-ant- validation)
Cell 03:  SMOKE TEST (run at 8:55am, 7 check categories)
Cell 04a: CUSTOMER_DB + TICKETS list + TICKETS_BY_ID + SLA_TABLE + KB
          + game_state init (10 fields, no streak)
          + PRE_GAME_RESPONSES guard + HUMAN_PLAYTHROUGH guard
Cell 04b: DEMO_SCRIPTS (T-001 2-step, T-003 3-step, T-BOSS 5-step,
          T-003-chatbot fallback, T-003-bad-agent capstone)
Cell 04c: TOOL_REGISTRY (7 tools)
Cell 05:  Tool functions (db_lookup, kb_search, escalate, etc.)
Cell 06:  SYSTEM_PROMPT + TOOL_PREREQUISITES + agent loop function
          + scoring engine + achievement triggers
          + force_plan_revision_banner check
          + loop visibility contract docstring

====== MANUAL MODE -- Run cells ONE AT A TIME ======

Cell 07:  Pre-game calibration (input() -- 2 questions -> PRE_GAME_RESPONSES)
Cell 08:  T-001 Manual Mode (input() loop with PLAN/ACT/OBSERVE, prereq blocking)
Cell 09:  T-003 Manual Mode (input() loop, seeded kb_search mistake, prereq blocking)
Cell 10:  Manual Mode summary + HUMAN_PLAYTHROUGH stored

====== AUTO MODE -- safe to Run All ======

Cell 11:  Chatbot fail on T-003 (live-first with stripped prompt, scripted fallback)
          + bridge sentence + time.sleep(3)
Cell 12:  AUTO MODE T-001 + post-ticket interstitial
Cell 12b: MY_PREDICTION_T003 = None  <-- participants edit before Cell 13
Cell 13:  AUTO MODE T-003 + human-vs-agent split-screen + interstitial
          (preamble: check MY_PREDICTION_T003 exists and is not None)
Cell 13b: MY_PREDICTION_TBOSS = None  <-- participants edit before Cell 14
Cell 14:  AUTO MODE T-BOSS (fanfare preamble + time.sleep(2) + live-preferred)
          (preamble: check MY_PREDICTION_TBOSS exists and is not None)
          + LIVE MODE banner if live + disclosure cell if scripted
Cell 15a: Replay Diff (hallucination_guard off: bad agent left, good agent right)
Cell 15b: print_final_score_screen() + PRE_GAME_RESPONSES reprint
          + 2 closing discussion questions
```

### Cell 03: Smoke Test (Final Form)

```python
errors = []

# game_state fields (streak intentionally absent -- removed Round 14)
REQUIRED_KEYS = ["score","strikes","tickets_resolved","current_ticket_idx",
                 "game_over","ticket_loop_counts","achievements",
                 "correct_predictions","flagged_escalations","t_boss_ran_live"]
for k in REQUIRED_KEYS:
    if k not in game_state: errors.append(f"game_state missing: '{k}'")

# DEMO_SCRIPTS coverage
for key in ["T-001","T-003","T-BOSS","T-003-chatbot","T-003-bad-agent"]:
    if key not in DEMO_SCRIPTS: errors.append(f"DEMO_SCRIPTS missing: '{key}'")

# TICKETS narrative consistency
assert len(TICKETS) == 3, "TICKETS must have 3 records"
for t in TICKETS:
    if not t["narrative_check"](CUSTOMER_DB):
        errors.append(f"{t['id']} narrative inconsistent with CUSTOMER_DB")

# SLA_TABLE
if not (SLA_TABLE.get("T-BOSS",{}).get("breached") == True):
    errors.append("SLA_TABLE: T-BOSS must show breached=True")

# KB coverage
for key in ["subscription_cancellation","b2b_account_escalation"]:
    if key not in KB: errors.append(f"KB missing: '{key}'")

for e in errors: print(e)
print("READY" if not errors else f"FIX {len(errors)} ISSUE(S) BEFORE PROCEEDING")
```

### Cell 04a: Game State Initialization

```python
game_state = {
    "score": 0, "strikes": 0,
    "tickets_resolved": [], "current_ticket_idx": 0,
    "game_over": False,
    "ticket_loop_counts": {},
    "achievements": [],
    "correct_predictions": 0,
    "flagged_escalations": [],
    "t_boss_ran_live": False
}

if "PRE_GAME_RESPONSES" not in dir():
    PRE_GAME_RESPONSES = {}

if "HUMAN_PLAYTHROUGH" not in dir():
    HUMAN_PLAYTHROUGH = {}
```

### Cell 07: Pre-Game Calibration

```python
print("Before we start -- answer these briefly:")
print("1. What's one decision in your team's support process that requires human judgment?")
print("2. What's the riskiest AI mistake in customer support?")

if not PRE_GAME_RESPONSES:
    q1 = input("Your answer to Q1: ")
    q2 = input("Your answer to Q2: ")
    PRE_GAME_RESPONSES["judgment_decision"] = q1
    PRE_GAME_RESPONSES["riskiest_mistake"] = q2
else:
    print("(Responses already recorded.)")
```

### Cell 11: Chatbot Fail

Live-first architecture: attempts a real API call with a stripped system prompt (no tools, no JSON schema). If it naturally hallucinates, that is the output. If it hedges or the API fails, the authored fallback fires:

```python
CHATBOT_PROMPT = "You are a helpful customer support agent. Answer the customer's question."
try:
    if os.environ.get("ANTHROPIC_API_KEY") and not FORCE_DEMO_MODE:
        raw_response = call_live_api_no_tools(ticket_text, CHATBOT_PROMPT)
        print(f"[LIVE CHATBOT]\n{raw_response}")
    else:
        raise Exception("no key")
except:
    print(DEMO_SCRIPTS["T-003-chatbot"]["output"])

print("\n[No tools called. No account checked. No prior compensation verified.]")
print("STRIKE: Duplicate compensation issued. Policy version cited: OUTDATED.\n")
print("The chatbot had the same ticket text the agent will have.")
print("Watch what the agent does differently -- and why.")
time.sleep(3)
```

**Authored chatbot fallback text:**
```
"Thank you for reaching out! Our standard refund policy for annual
subscriptions allows returns within 30 days of purchase. Since you
purchased recently, you should be eligible for a full refund. I've
flagged your account for processing -- you'll hear back within 3-5
business days."
```

### Cell 12b/13b: Prediction Cells

```python
# Cell 12b -- edit before running Cell 13
# What tool does the agent call FIRST on T-003?
MY_PREDICTION_T003 = None  # options: "db_lookup", "kb_search", "request_info", "check_sla_status"
# Run this cell, then run Cell 13
```

### Cell 13/14 Preamble: Prediction Guards

```python
# In Cell 13 preamble:
if "MY_PREDICTION_T003" not in dir():
    raise ValueError("Run Cell 12b first -- edit your prediction before continuing.")
assert MY_PREDICTION_T003 is not None, "Change None to your guess in Cell 12b, then re-run."

# Score the prediction
if MY_PREDICTION_T003 in ticket["prediction_answer"]:
    game_state["correct_predictions"] += 1
    print("You think like an agent.")
else:
    print("The agent surprised you -- why?")
```

### Cell 15a: Replay Diff

```python
def render_replay_diff():
    good_steps = DEMO_SCRIPTS["T-003"]            # 3-step db_lookup-first path
    bad_output  = DEMO_SCRIPTS["T-003-bad-agent"]["output"]  # fabricated policy text

    print("BAD AGENT (hallucination_guard: OFF) | GOOD AGENT (hallucination_guard: ON)")
    print("-" * 50)
    print(bad_output)
    print("\n---vs---\n")
    for step in good_steps:
        print(f"[REFLECT] {step['reasoning'][:80]}...")
        print(f"[ACT]     {step['next_tool']}")
    print("\nCorrect resolution: confirmed prior credit, no duplicate issued.")
```

**Bad agent authored output (from Round 5, keyed as `DEMO_SCRIPTS["T-003-bad-agent"]`):**
```
"Under our Customer Satisfaction Guarantee, any customer who contacts
support within 90 days of an issue is eligible for a full refund or
store credit, at our discretion. I've initiated a $47.00 refund to
your original payment method. You'll receive confirmation within
3-5 business days."

[KB verification: "Customer Satisfaction Guarantee" -> NO RESULTS FOUND]
[DB verification: prior_compensation=$25 issued 6 weeks ago -> DUPLICATE]
STRIKE: Duplicate compensation + fabricated policy cited.
```

### Cell 15b: Final Score + Closing Discussion

```python
def print_final_score_screen(game_state):
    counts = game_state["ticket_loop_counts"]
    worst = max(counts, key=lambda k: counts[k]) if counts else "N/A"
    best  = min(counts, key=lambda k: counts[k]) if counts else "N/A"
    rank = ("SENIOR AGENT" if game_state["score"] >= 400
            else "AGENT" if game_state["score"] >= 200
            else "TRAINEE")
    print("GAME COMPLETE -- SUPPORTDESK ROYALE")
    print("-" * 42)
    print(f"Final Score:  {game_state['score']} pts    Rank: {rank}")
    print(f"Strikes:      {game_state['strikes']}          "
          f"Achievements: {', '.join(game_state['achievements']) or 'None'}")
    print(f"Predictions:  {game_state['correct_predictions']}/3 correct  "
          f"(Human Intuition Score)")
    print(f"\nBest moment:  {best} -- fewest loops, cleanest resolution.")
    print(f"Worst moment: {worst} -- most loops. The agent struggled here too.")
    print("-" * 42)

print_final_score_screen(game_state)

print("\n--- CLOSING DISCUSSION ---")
print(f"\nYou said before we started:")
print(f"   '{PRE_GAME_RESPONSES.get('judgment_decision', '(not recorded)')}'")
print(f"   '{PRE_GAME_RESPONSES.get('riskiest_mistake', '(not recorded)')}'")
print("\nQ1: Where did the agent earn its points? What did it check that you didn't?")
print("\nQ2: What would the agent need to know to resolve the BOSS ticket directly next time?")
```

**Note:** Q2 is Devil's Advocate's version, verbatim. The original "Should the agent have handled it?" question was permanently cut in Round 10. The closing ends on system design, not limitation acknowledgment. This is the ROI conversation that funds the next workshop.

### Facilitator verbal beats (not in the notebook -- memorized)

**Cell 11 (after the 3-second sleep):** *"Same ticket. No account check. Confident and wrong. This is what your current assistant gives you."*

**T-003 split-screen:** *"The agent checked your account history before reading the rulebook. You read the rulebook first. At 500 tickets a day, which process do you want?"*

**Cell 15b (after pre-game answers reprint):** *"You said that. The question isn't whether AI can handle it -- it's what it would need to do it reliably for your specific business."*

---

## 11. KEY AGENTIC TEACHING MOMENTS

### Moment 1: "The Machine Doesn't Know What It Doesn't Know" (Cell 11)

The chatbot confidently outputs a wrong answer with zero hedging. Facilitator asks: *"Why did it fail -- bad information, or bad process?"* The answer is bad process: it had no tools, no state lookup, no verification step. The bridge sentence prints: *"The chatbot had the same ticket text the agent will have. Watch what the agent does differently -- and why."*

### Moment 2: "It Changed Its Mind" (T-003, Cell 13)

The PLAN REVISION banner fires when the agent discovers prior compensation in the DB. The facilitator pauses and asks the room: *"What would your current chatbot have done here?"* The answer: applied the policy and issued duplicate compensation. The phrase "PLAN REVISION" appears visibly. That delta -- plan announced, plan abandoned, new plan formed -- is what separates an agent from a chatbot.

### Moment 3: The Split-Screen (T-003, Cell 13)

Participants see their own tool path next to the agent's. The thesis sentence prints automatically. This is personal, not abstract. The message is not "AI beat you" but "here's the habit the agent has that you didn't."

### Moment 4: Synthesis Under Pressure (T-BOSS, Cell 14)

The BOSS ticket requires the agent to synthesize across five data sources and choose between two valid terminal paths. The REFLECT step names both paths before choosing one. This is judgment, not lookup. When the live mode banner fires -- *"This reasoning was not scripted"* -- the room sees genuine agent reasoning.

### Moment 5: The Capstone Contrast (Cell 15a)

The Replay Diff shows the same ticket handled by a bad agent (hallucination_guard off) and a good agent. Plausible corporate language on the left, three-step DB-first resolution on the right. Two simultaneous errors: fabricated policy + duplicate compensation. Every manager has *sent* an email like the bad agent's output from a junior rep.

### Moment 6: The Closing Question (Cell 15b)

Pre-game answers reprint. The facilitator asks: *"What would the agent need to know to resolve the BOSS ticket directly next time?"* Managers are designing the system's improvement, not confirming its limitations. This is the ROI conversation.

---

## 12. TECHNICAL REQUIREMENTS

### Dependencies

```
anthropic (pip install anthropic -q)
```

No other dependencies. No `ipywidgets`. No `scikit-learn`. Print-based output with `time.sleep()` for dramatic pauses.

### API Key Handling

- Anthropic only (`sk-ant-` prefix validated)
- `getpass.getpass()` for secure entry
- `FORCE_DEMO_MODE` flag for explicit override
- Priority: API key present + FORCE_DEMO_MODE=False = live mode
- Silent fallback to DEMO_SCRIPTS on API failure
- Prominent banner when running scripted

### DEMO_MODE Architecture

DEMO_SCRIPTS are first-class teaching artifacts, not just fallbacks. They are hand-crafted to demonstrate specific agentic behaviors (self-correction, synthesis, plan revision). Five keys:

| Key | Purpose | Steps |
|---|---|---|
| `T-001` | Tutorial path (locked account, identity verification) | 2 steps + terminal |
| `T-003` | Trap door path (DB-first, prior compensation discovery) | 3 steps |
| `T-BOSS` | Synthesis path (five tools, two paths considered) | 5 steps |
| `T-003-chatbot` | Confident wrong chatbot output for Cell 11 fallback | 1 output block |
| `T-003-bad-agent` | Fabricated policy hallucination for Cell 15a capstone | 1 output block |

### Parse Failure Handling

If the LLM returns malformed JSON:
```
[AGENT STUMBLED] Response parsing failed.
Raw output: "I think I should check the database first..."
Retrying with structured prompt reinforcement... (attempt 2/2)
```
After 2 failures, DEMO_SCRIPTS fallback fires. The game never crashes. The parse failure is surfaced as a teaching moment about agent reliability.

### Data Initialization Sweep (every structure referenced by Cell 05/06)

| Structure | Initialized in |
|---|---|
| `CUSTOMER_DB` | Cell 04a |
| `KB` | Cell 04a |
| `SLA_TABLE` | Cell 04a |
| `TICKETS` / `TICKETS_BY_ID` | Cell 04a |
| `game_state` | Cell 04a |
| `PRE_GAME_RESPONSES` | Cell 04a (guard) |
| `HUMAN_PLAYTHROUGH` | Cell 04a (guard) |
| `DEMO_SCRIPTS` | Cell 04b |
| `TOOL_REGISTRY` | Cell 04c |
| `TOOL_PREREQUISITES` | Cell 06 preamble |

No `NameError` is possible after Cell 04a/b/c and Cell 06 execute.

### Build Order

```
Cell 06 -> 04a/b/c -> 03 -> 08-09 -> 11 -> 12-14 -> 15a-15b
```

Cell 06 (the agent loop) is the load-bearing wall. Everything else is rooms. The smoke test (Cell 03) is the integration gate. When it prints `READY`, the workshop is ready. Estimated build time: 2 days.

---

## 13. RISKS & MITIGATIONS

| Risk | Mitigation |
|---|---|
| **API key expires overnight** | FORCE_DEMO_MODE defaults to False but DEMO_SCRIPTS fire automatically on API failure. Silent fallback. Facilitator owns verbal framing. |
| **LLM returns offensive/embarrassing content** | Content filter on all LLM output before display. DEMO_SCRIPTS provide authored fallback for all three tickets. |
| **LLM hallucinates confidently in live mode** | Scoring engine checks against ground truth lambdas over CUSTOMER_DB. Wrong answers are caught structurally regardless of how confident the LLM sounds. |
| **Participant runs "Run All" during Manual Mode** | Section headers with clear warnings. `input()` blocks execution visibly. Cell 07 moved inside Manual Mode section. |
| **`HUMAN_PLAYTHROUGH` wiped by cell rerun** | Guard: `if "HUMAN_PLAYTHROUGH" not in dir()`. Cell 04a does not reset it on re-execution. |
| **`PRE_GAME_RESPONSES` overwritten** | Same guard pattern in Cell 04a. Responses written once, read at closing. |
| **Prediction cell not edited before AUTO Mode** | `if "MY_PREDICTION_T003" not in dir(): raise ValueError(...)`. Falls back to `assert is not None` for edited-but-unchanged case. Readable error messages, no stack traces. |
| **Participant enters wrong API key type (OpenAI)** | `sk-ant-` prefix check with helpful error message and fallback to DEMO mode. |
| **DB values contradict ticket narrative** | `narrative_check` lambdas in TICKETS dicts, validated by smoke test at 8:55am. Example: `days_since_purchase <= 30` for T-003. |
| **Someone asks "Is this live or scripted?"** | Disclosure cell below T-BOSS output (honest on demand). LIVE MODE banner when it runs live. No deception -- intellectual honesty is non-negotiable. |
| **Skeptical VP asks "Why can't you just write if-else rules?"** | T-003 requires cross-referencing account history with ticket text. T-BOSS requires synthesis across 5 data sources. No lookup table covers these combinations. |
| **Half the room free-rides during Manual Mode** | Manual Mode strikes count (real consequences). Teams of 3-4 per notebook (social pressure). Prediction cells give everyone skin in the game during AUTO Mode. |
| **Session runs over time** | 111-minute structured runtime + 20-minute buffer = 130 min. Cut list: prediction mechanic (appendix), knowledge audit (facilitator speaks it), achievement system (final screen only), tickets 2 and 4 (already cut for MVP). Non-negotiable: the Replay Diff capstone in Cell 15a. |
| **Facilitators leave DEMO_MODE on permanently** | Prominent `SCRIPTED MODE` banner on every ticket. `FORCE_DEMO_MODE` requires explicit opt-in. Live mode is the default when API key is present. |
| **`SLA_TABLE` / `KB` / `TICKETS` uninitialized** | All initialized in Cell 04a. Smoke test in Cell 03 validates presence and consistency of every data structure before participants arrive. |

---

## 14. UNRESOLVED QUESTIONS

1. **`kb_search` matching logic:** The KB is specified as a simple dict but the exact matching function (exact key match, keyword substring match, or fuzzy match) is left to the build sprint. The seeded mistake on T-003 requires that searching "refund" or "subscription" returns the `subscription_cancellation` entry.

2. **`RESOLVE_WITH_BRIEF` scoring in live mode:** This path exists only in live mode (no DEMO_SCRIPTS coverage). The exact content-matching logic for validating the email draft's five required context fields was not fully specified. AI Engineer determines during build whether to use keyword presence checks or a more relaxed validation.

3. **`AGENT_CONFIG` knobs:** The `hallucination_guard`, `escalation_threshold`, and `policy_strictness` knobs were discussed extensively for participant experimentation. The `hallucination_guard` knob works in Cell 15a via DEMO_SCRIPTS. The exact mechanism by which the other knobs modify agent behavior (system prompt modification? temperature change?) was not fully specified. These are appendix material for participant experimentation after the core session.

4. **Extending beyond 3 tickets:** The MVP cuts tickets 2 and 4 (easy-difficulty). If time permits, these can be added: an "Easy: wrong item shipped" ticket (DB + email_draft) and a "Medium: refund outside policy with high-LTV angry customer" ticket. The single-source ticket dict schema makes adding tickets straightforward -- one dict per ticket with all fields co-located.

5. **CUSTOMER_DB field completeness:** The three DB records are specified by what DEMO_SCRIPTS reference. AI Engineer may need to add minor fields (e.g., email addresses, order numbers) during build if tool functions require them. These are build-time implementation details.

6. **Pre-workshop communications:** The pre-workshop email must tell participants to obtain a free Anthropic API key (link to console.anthropic.com included). This is a facilitation logistics item, not a design decision.
