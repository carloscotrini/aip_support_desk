# src/cells/reentry.py
"""
"Next Morning" re-entry cell — demonstrates stateful persistence by resuming
a previously handled ticket with new information.
"""

from __future__ import annotations

from src.agent.loop import run_agent


# ---------------------------------------------------------------------------
# Pre-scripted demo content
# ---------------------------------------------------------------------------

NEXT_MORNING_MESSAGE = {
    "from": "Marcus Thiele",
    "role": "Senior Account Manager",
    "body": (
        "I've reviewed the Northgate Logistics account. The Q1 billing error "
        "has been confirmed — we overcharged $2,340 due to a tier migration "
        "glitch. Credit memo has been issued and will appear on their next "
        "statement. I've also scheduled a call with their CFO for Thursday to "
        "discuss the contract renewal. Please draft a confirmation email to "
        "the customer referencing credit memo #CM-2024-0847."
    ),
}

REENTRY_DEMO_RESPONSES = [
    {
        "reasoning": (
            "Marcus confirmed the billing error and issued a credit memo "
            "(#CM-2024-0847) for $2,340. I need to draft a professional "
            "confirmation email to the customer referencing the credit memo "
            "and the upcoming Thursday call with their CFO."
        ),
        "next_tool": "send_email",
        "tool_args": {
            "to": "j.whitfield@northgatelogistics.com",
            "subject": "Re: Q1 Billing Dispute — Credit Memo Issued",
            "body": (
                "Dear Mr. Whitfield,\n\n"
                "Thank you for your patience while we investigated the Q1 "
                "billing discrepancy on your account.\n\n"
                "Our Senior Account Manager, Marcus Thiele, has completed his "
                "review and confirmed that an overcharge of $2,340 occurred "
                "due to a tier migration issue. A credit memo (#CM-2024-0847) "
                "has been issued and will appear on your next statement.\n\n"
                "Additionally, Marcus has scheduled a call with your CFO for "
                "Thursday to discuss your contract renewal and ensure we have "
                "the correct service tier going forward.\n\n"
                "Please don't hesitate to reach out if you have any further "
                "questions.\n\n"
                "Best regards,\n"
                "Meridian Fleet Solutions Support"
            ),
        },
        "confidence": 0.95,
        "resolution_status": "RESOLVED",
    }
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resume_agent(
    prior_state: dict,
    new_message: str,
    llm_client=None,
    demo_responses: list[dict] | None = None,
) -> dict:
    """Resume an agent with new external information.

    Args:
        prior_state: The ``agent_state`` dict returned by a previous
            ``run_agent`` call.
        new_message: A new message string (e.g. a human reply) to inject.
        llm_client: An LLM client for live mode.
        demo_responses: Pre-scripted responses for demo / offline mode.

    Returns:
        The final ``agent_state`` dict after the resumed loop completes.
    """
    # -- Inject the new message into prior state --------------------------------
    prior_steps = len(prior_state.get("steps_taken", []))

    prior_state["steps_taken"].append({
        "phase": "EXTERNAL_INPUT",
        "tool": None,
        "inputs": {},
        "outputs": new_message,
        "reasoning": "New external message received.",
    })

    prior_state["status"] = "INVESTIGATING"

    # -- Print header -----------------------------------------------------------
    _print_header(new_message, prior_steps)

    # -- Re-enter the agent loop ------------------------------------------------
    # We pass the modified prior_state as the ticket so run_agent picks up
    # existing context. We preserve prior steps by pre-populating the state.
    updated_state = _run_resumed_loop(prior_state, llm_client, demo_responses)

    # -- Pedagogical print ------------------------------------------------------
    _print_insight(prior_steps)

    return updated_state


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_resumed_loop(
    state: dict,
    llm_client,
    demo_responses: list[dict] | None,
) -> dict:
    """Re-enter run_agent while preserving existing state."""
    if llm_client is None and demo_responses is None:
        raise ValueError(
            "Either llm_client or demo_responses must be provided."
        )

    from src.tools.registry import dispatch_tool  # noqa: F811
    import json

    MAX_ITERATIONS = 10

    iteration = 0
    while state["status"] != "RESOLVED" and iteration < MAX_ITERATIONS:
        iteration += 1

        # PLAN
        if demo_responses:
            llm_response = demo_responses.pop(0)
        else:
            from src.agent.loop import _call_llm
            llm_response = _call_llm(state, llm_client)

        reasoning = llm_response.get("reasoning", "")
        next_tool = llm_response.get("next_tool", "")
        tool_args = llm_response.get("tool_args", {})
        new_confidence = llm_response.get("confidence", state["confidence"])
        new_status = llm_response.get("resolution_status", state["status"])

        print(f"[AGENT THINKING] {reasoning}")
        print(
            f"[AGENT STATUS]   Confidence: {int(new_confidence * 100)}% "
            f"| Status: {new_status}"
        )

        # ACT
        args_display = ", ".join(
            f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
            for k, v in tool_args.items()
        )
        print(f"[AGENT ACTION]   Calling {next_tool}({args_display})")

        tool_result = dispatch_tool(next_tool, **tool_args)

        step = {
            "phase": len(state["steps_taken"]) + 1,
            "tool": next_tool,
            "inputs": tool_args,
            "outputs": tool_result,
            "reasoning": reasoning,
        }
        state["steps_taken"].append(step)

        # OBSERVE
        state["context"].append(
            {"role": "tool", "tool": next_tool, "content": tool_result}
        )

        result_summary = json.dumps(tool_result, default=str)
        if len(result_summary) > 200:
            result_summary = result_summary[:200] + "..."
        print(f"[AGENT OBSERVE]  Result: {result_summary}")

        # REFLECT
        prev_confidence = state["confidence"]
        state["confidence"] = new_confidence
        state["status"] = new_status

        if new_confidence < prev_confidence:
            print(
                f"[AGENT REFLECT]  Confidence dropped: "
                f"{int(prev_confidence * 100)}% → {int(new_confidence * 100)}%. "
                f"Re-planning."
            )

        if state["status"] == "RESOLVED":
            n_steps = len(state["steps_taken"])
            print(
                f"[AGENT RESOLVED] Ticket resolved in {n_steps} total steps. "
                f"Final confidence: {int(state['confidence'] * 100)}%"
            )

    return state


def _print_header(new_message: str, prior_steps: int) -> None:
    """Print the re-entry header box."""
    print(
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  📬 NEW MESSAGE RECEIVED — Resuming agent...           ║\n"
        "╠══════════════════════════════════════════════════════════╣\n"
        f"║  From: {NEXT_MORNING_MESSAGE['from']}, {NEXT_MORNING_MESSAGE['role']:<28s}║\n"
        f"║  \"{_truncate(new_message, 50)}\" ║\n"
        "╠══════════════════════════════════════════════════════════╣\n"
        f"║  Prior context: {prior_steps} steps from previous session{' ' * (11 - len(str(prior_steps)))}║\n"
        "║  Resuming PLAN → ACT → OBSERVE → REFLECT loop...       ║\n"
        "╚══════════════════════════════════════════════════════════╝"
    )


def _print_insight(prior_steps: int) -> None:
    """Print the pedagogical insight box."""
    print(
        "\n"
        "╔══════════════════════════════════════════════════════════╗\n"
        "║  💡 KEY INSIGHT: Stateful Persistence                   ║\n"
        "╠══════════════════════════════════════════════════════════╣\n"
        "║  The agent resumed with its full prior context:          ║\n"
        f"║  • Remembered all {prior_steps} previous steps{' ' * (25 - len(str(prior_steps)))}║\n"
        "║  • Understood Marcus's reply in context                  ║\n"
        "║  • Drafted a response referencing prior investigation    ║\n"
        "║                                                          ║\n"
        "║  A stateless chatbot would have started from scratch.    ║\n"
        "╚══════════════════════════════════════════════════════════╝"
    )


def _truncate(text: str, max_len: int) -> str:
    """Truncate text and pad/trim to fit the box width."""
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text
