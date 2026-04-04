# src/agent/loop.py
"""
Core agent loop with PLAN -> ACT -> OBSERVE -> REFLECT cycle
and confidence tracking for Meridian Fleet Solutions support desk.
"""

from __future__ import annotations

import json

from src.tools.registry import TOOL_SCHEMAS, dispatch_tool
from src.data.tickets import TICKETS  # noqa: F401 — imported so callers can grab tickets via this module

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIDENCE_THRESHOLD = 0.8
MAX_ITERATIONS = 10

SYSTEM_PROMPT = """\
You are an AI customer-support agent for **Meridian Fleet Solutions**, a fleet-management \
platform serving logistics companies. Your job is to investigate incoming support tickets, \
use the tools at your disposal to gather facts, and resolve or escalate each ticket.

## How you work

You follow a strict **PLAN → ACT → OBSERVE → REFLECT** loop:

1. **PLAN** — Read the ticket and everything you know so far. Decide which tool to call \
next and why. State your reasoning in plain language.
2. **ACT** — Call exactly one tool per iteration.
3. **OBSERVE** — Read the tool's output carefully.
4. **REFLECT** — Update your confidence (0–100 %) in being able to resolve the ticket. \
If new information contradicts earlier findings, drop your confidence and re-plan.

## Output format

Every response must be a single JSON object with these five fields:

```json
{
    "reasoning":         "<1-3 sentences explaining your current thinking>",
    "next_tool":         "<tool name to call>",
    "tool_args":         { ... },
    "confidence":        0.85,
    "resolution_status": "INVESTIGATING | DRAFTING | ESCALATING | RESOLVED"
}
```

## Confidence rules

- Start at a low confidence and increase it only as evidence accumulates.
- **Drop** confidence whenever a tool result contradicts your earlier assumption.
- Only set status to `RESOLVED` when confidence >= 80 % and you have taken all \
necessary actions (e.g., sent an email, escalated where needed).

## Escalation policy

- If the issue involves billing disputes over $500, contract termination threats, \
or anything that exceeds a front-line agent's authority, **escalate** to the \
appropriate manager rather than guessing.
- Always include a structured summary when escalating.

## Tone

- Professional, clear, and concise.
- A non-technical manager should be able to read your reasoning and understand \
every step.
"""


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

def run_agent(
    ticket: dict,
    llm_client=None,
    demo_responses: list[dict] | None = None,
) -> dict:
    """Run the PLAN-ACT-OBSERVE-REFLECT loop on a single ticket.

    Args:
        ticket: A ticket dict (from TICKETS).
        llm_client: An LLM client for live mode. Ignored when *demo_responses*
            is provided.
        demo_responses: Pre-scripted LLM responses for demo / offline mode.
            Each element must be a dict with the five fields described in the
            system prompt.

    Returns:
        The final ``agent_state`` dict.
    """
    if llm_client is None and demo_responses is None:
        raise ValueError(
            "Either llm_client or demo_responses must be provided."
        )

    agent_state: dict = {
        "ticket": ticket,
        "status": "INVESTIGATING",
        "confidence": 0.0,
        "steps_taken": [],
        "context": [],
    }

    iteration = 0

    while agent_state["status"] != "RESOLVED" and iteration < MAX_ITERATIONS:
        iteration += 1

        # ── PHASE 1: PLAN ──────────────────────────────────────────────
        if demo_responses:
            llm_response = demo_responses.pop(0)
        else:
            llm_response = _call_llm(agent_state, llm_client)

        reasoning = llm_response.get("reasoning", "")
        next_tool = llm_response.get("next_tool", "")
        tool_args = llm_response.get("tool_args", {})
        new_confidence = llm_response.get("confidence", agent_state["confidence"])
        new_status = llm_response.get("resolution_status", agent_state["status"])

        print(f"[AGENT THINKING] {reasoning}")
        print(
            f"[AGENT STATUS]   Confidence: {int(new_confidence * 100)}% "
            f"| Status: {new_status}"
        )

        # ── PHASE 2: ACT ───────────────────────────────────────────────
        args_display = ", ".join(
            f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
            for k, v in tool_args.items()
        )
        print(f"[AGENT ACTION]   Calling {next_tool}({args_display})")

        tool_result = dispatch_tool(next_tool, **tool_args)

        step = {
            "phase": iteration,
            "tool": next_tool,
            "inputs": tool_args,
            "outputs": tool_result,
            "reasoning": reasoning,
        }
        agent_state["steps_taken"].append(step)

        # ── PHASE 3: OBSERVE ────────────────────────────────────────────
        agent_state["context"].append(
            {"role": "tool", "tool": next_tool, "content": tool_result}
        )

        result_summary = json.dumps(tool_result, default=str)
        if len(result_summary) > 200:
            result_summary = result_summary[:200] + "..."
        print(f"[AGENT OBSERVE]  Result: {result_summary}")

        # ── PHASE 4: REFLECT ───────────────────────────────────────────
        prev_confidence = agent_state["confidence"]
        agent_state["confidence"] = new_confidence
        agent_state["status"] = new_status

        if new_confidence < prev_confidence:
            print(
                f"[AGENT REFLECT]  Confidence dropped: "
                f"{int(prev_confidence * 100)}% → {int(new_confidence * 100)}%. "
                f"Re-planning."
            )

        if agent_state["status"] == "RESOLVED":
            n_steps = len(agent_state["steps_taken"])
            print(
                f"[AGENT RESOLVED] Ticket resolved in {n_steps} steps. "
                f"Final confidence: {int(agent_state['confidence'] * 100)}%"
            )

    return agent_state


# ---------------------------------------------------------------------------
# LLM helper
# ---------------------------------------------------------------------------

def _call_llm(agent_state: dict, llm_client) -> dict:
    """Build prompts from agent state and call the LLM.

    Supports:
    - An ``anthropic.Anthropic`` client (duck-typed: must have
      ``messages.create``).
    - Any callable that accepts ``(system, messages, tools)`` keyword args
      and returns a dict with the five expected fields.

    Returns:
        A dict with keys: reasoning, next_tool, tool_args, confidence,
        resolution_status.
    """
    ticket = agent_state["ticket"]

    # Build the user message with ticket + history
    user_parts = [
        f"## Current Ticket\n"
        f"- **ID:** {ticket['ticket_id']}\n"
        f"- **Customer:** {ticket['customer_id']}\n"
        f"- **Subject:** {ticket['subject']}\n"
        f"- **Body:** {ticket['body']}\n",
    ]

    if agent_state["steps_taken"]:
        user_parts.append("## Steps Taken So Far\n")
        for step in agent_state["steps_taken"]:
            user_parts.append(
                f"- **Step {step['phase']}** — called `{step['tool']}` "
                f"with {json.dumps(step['inputs'], default=str)}\n"
                f"  Result: {json.dumps(step['outputs'], default=str)[:300]}\n"
            )

    user_parts.append(
        f"\n## Current State\n"
        f"- Status: {agent_state['status']}\n"
        f"- Confidence: {agent_state['confidence']}\n"
        f"\nRespond with a single JSON object containing: "
        f"reasoning, next_tool, tool_args, confidence, resolution_status."
    )

    user_message = "\n".join(user_parts)

    # --- Anthropic client path ---
    if hasattr(llm_client, "messages"):
        tools_for_api = [
            {
                "name": s["name"],
                "description": s["description"],
                "input_schema": s["parameters"],
            }
            for s in TOOL_SCHEMAS
        ]

        response = llm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools_for_api,
            messages=[{"role": "user", "content": user_message}],
        )

        # Extract text content from the response
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text

        return json.loads(text)

    # --- Callable interface path ---
    if callable(llm_client):
        return llm_client(
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            tools=TOOL_SCHEMAS,
        )

    raise TypeError(
        f"llm_client must be an Anthropic client or a callable, "
        f"got {type(llm_client)}"
    )
