# src/content/reflection_prompts.py

"""
Reflection prompts and facilitator pause-point notes for the
Agentic AI Customer Support Desk exercise.

Usage:
    from src.content.reflection_prompts import REFLECTION_PROMPTS_MD, PAUSE_POINTS
"""

# ---------------------------------------------------------------------------
# Markdown string for the final reflection cell (Section 11)
# ---------------------------------------------------------------------------

REFLECTION_PROMPTS_MD = """\
## Reflection & Discussion

Take a few minutes to discuss the following questions with your group.\
 They move from what you just observed to what it could mean for your organisation.

---

### 1. Observation
**What did the agent do differently from the chatbot when handling the same ticket?**
Think about the number of steps, the sources of information it consulted,\
 and the structure of its final response.

### 2. Mechanism
**Why did the agent need to call multiple tools, and could a chatbot have done the same?**
Consider what it means for a system to plan its own sequence of actions\
 rather than producing a single response.

### 3. Self-Correction
**What happened when the agent retrieved the wrong document?**\
 **How did it detect the mistake and recover?**
Pay attention to the confidence score and the moment the agent chose to\
 re-query instead of trusting its first result.

### 4. Authority & Escalation
**How did the agent decide to escalate rather than attempt a resolution on its own?**
Think about the role of policy rules, authorisation limits, and the\
 structured escalation artifact it produced.

### 5. Business Impact
**Where in your own organisation could an agentic system like this\
 create the most value?**
Consider processes that involve multiple data sources, decision steps,\
 or handoffs between people.

### 6. Risk & Governance
**What risks do you see in deploying an agent that makes autonomous\
 decisions in customer-facing scenarios?**
Think about accountability, error handling, data privacy, and the\
 boundary between automation and human judgement.

### 7. Next Steps
**What would you need to evaluate before piloting agentic AI in your team?**
Consider data readiness, process documentation, success metrics, and\
 the change-management challenges you would face.
"""

# ---------------------------------------------------------------------------
# Facilitator pause-point notes keyed by notebook section number (1–11)
# ---------------------------------------------------------------------------

PAUSE_POINTS = {
    1: (
        "Setup — no pause needed. Walk the room to make sure every "
        "participant's cells execute without errors before moving on."
    ),
    2: (
        "Knowledge Base — Pause briefly. Ask: 'Take a look at these five "
        "documents. Do you notice anything that might be missing or "
        "incomplete?' This primes participants to spot the gaps the agent "
        "will encounter later."
    ),
    3: (
        "Mock Database — Quick check: ensure participants see how customer "
        "and device records are structured. Ask: 'Why might an agent need "
        "this data in addition to the knowledge base?'"
    ),
    4: (
        "Tool Registry — Highlight that every tool prints a visible trace. "
        "Ask: 'Which of these tools would a traditional chatbot have access "
        "to?' (Answer: none of them.)"
    ),
    5: (
        "The Frustrated Chatbot — PAUSE HERE. Give participants a full "
        "minute to read the chatbot's response. Ask: 'Would you trust this "
        "answer if you were the customer? What is it missing?' Collect two "
        "or three responses before continuing."
    ),
    6: (
        "RAG in Isolation — Pause after the retrieval result is displayed. "
        "Ask: 'We got a document back — does that count as a solution, or "
        "just a lookup?' Reinforce the label: 'This is a lookup, not a "
        "decision.'"
    ),
    7: (
        "The Agent Loop — This is the core of the exercise. Walk through "
        "the printed trace line by line. Pause after each Plan/Act/Observe/"
        "Reflect cycle and ask: 'What did the agent just decide, and why?' "
        "Highlight any confidence-score changes and re-planning moments."
    ),
    8: (
        "Side-by-Side Comparison — Let the visual speak for itself for 30 "
        "seconds, then ask: 'What stands out when you compare the two "
        "columns?' Draw attention to the number of steps and the quality "
        "of the final output."
    ),
    9: (
        "Ticket Variations — Invite participants to change ACTIVE_TICKET "
        "and re-run the agent loop. Suggest T4 for the self-correction "
        "demo and T5 for the escalation demo. Allow 2–3 minutes of "
        "free exploration."
    ),
    10: (
        "Next-Morning Re-Entry (optional) — If time permits, run this "
        "cell to show stateful persistence. Ask: 'How is this different "
        "from starting a new chat session?' Emphasise that the agent "
        "remembers every prior step."
    ),
    11: (
        "Reflection Prompts — Switch from demo to discussion. Read each "
        "question aloud and give the group 1–2 minutes per question. "
        "Close by asking participants to name one concrete next step they "
        "will take back to their team."
    ),
}
