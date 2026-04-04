"""Contrast cells: frustrated chatbot and RAG-only retrieval.

These produce "before" outputs that set up the aha-moment
when the full agent loop is demonstrated.
"""

from src.tools.search_kb import search_kb

# ---------------------------------------------------------------------------
# Pre-scripted demo responses — deliberately generic / wrong
# ---------------------------------------------------------------------------

CHATBOT_DEMO_RESPONSES = {
    "T1": (
        "Thank you for reaching out! To export your mileage report, "
        "please log in to the Meridian Fleet Solutions customer portal "
        "and navigate to the Reports section. You should be able to "
        "download your report from there. Let us know if you need "
        "further assistance!"
    ),
    "T2": (
        "We're sorry to hear about the connectivity issue. Please try "
        "power-cycling the device by unplugging it for 30 seconds and "
        "plugging it back in. If the problem persists, check that the "
        "SIM card is properly seated. You can also try moving the device "
        "to an area with better cellular coverage."
    ),
    "T3": (
        "Thank you for contacting Meridian Fleet Solutions support. "
        "We apologize for the inconvenience regarding your invoice. "
        "Please review your billing statement in the customer portal "
        "and let us know if you still see a discrepancy. We're happy "
        "to help!"
    ),
    "T4": (
        "Great question! Getting started with Meridian Fleet Solutions "
        "is easy. Our onboarding process includes a dedicated account "
        "manager, device installation scheduling, and a complimentary "
        "training session for your team. We'll have you up and running "
        "in no time! Would you like to schedule your kickoff call?"
    ),
    "T5": (
        "Thank you for your feedback. We value your business and want "
        "to ensure you have the best experience with our services. "
        "A member of our billing team will review your account and "
        "get back to you within 3-5 business days. We appreciate "
        "your patience!"
    ),
}

# ---------------------------------------------------------------------------
# Box-drawing helpers
# ---------------------------------------------------------------------------

_BOX_WIDTH = 58


def _box_line(text: str, pad: int = 2) -> str:
    inner = " " * pad + text
    return "║" + inner.ljust(_BOX_WIDTH) + "║"


def _box_top() -> str:
    return "╔" + "═" * _BOX_WIDTH + "╗"


def _box_mid() -> str:
    return "╠" + "═" * _BOX_WIDTH + "╣"


def _box_bot() -> str:
    return "╚" + "═" * _BOX_WIDTH + "╝"


def _box_empty() -> str:
    return "║" + " " * _BOX_WIDTH + "║"


def _wrap_text(text: str, width: int) -> list[str]:
    """Simple word-wrap into lines of at most *width* characters."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}" if current else word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_frustrated_chatbot(
    ticket: dict,
    llm_client=None,
    demo_response: str | None = None,
) -> str:
    """Simulate a plain chatbot response (no tools, no loop).

    Returns the response string.
    """
    # --- Obtain response ------------------------------------------------
    if demo_response is not None:
        response = demo_response
    elif llm_client is not None:
        messages = llm_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=(
                "You are a customer support agent for Meridian Fleet Solutions. "
                "Answer the customer's question."
            ),
            messages=[{"role": "user", "content": ticket["body"]}],
        )
        response = messages.content[0].text
    else:
        # Fall back to the pre-scripted demo response
        response = CHATBOT_DEMO_RESPONSES.get(
            ticket["ticket_id"],
            "I'm sorry, I don't have enough information to help with that.",
        )

    # --- Print styled box -----------------------------------------------
    content_width = _BOX_WIDTH - 4  # 2 padding each side
    wrapped = _wrap_text(response, content_width)

    lines = [
        _box_top(),
        _box_line("\U0001f916 CHATBOT RESPONSE (no tools, no reasoning loop)"),
        _box_mid(),
        _box_empty(),
    ]
    for wl in wrapped:
        lines.append(_box_line(f'"{wl}' if wl is wrapped[0] else f" {wl}", pad=2))
    # close the quote on the last line
    lines[-1] = lines[-1].rstrip("║").rstrip() + '"' + " " * 2 + "║"
    # re-pad to box width
    inner = lines[-1][1:-1]
    lines[-1] = "║" + inner.ljust(_BOX_WIDTH) + "║"

    lines.append(_box_empty())
    lines.append(_box_bot())

    print("\n".join(lines))
    return response


def run_rag_only(ticket: dict, top_k: int = 3) -> list[dict]:
    """Call search_kb directly — no reasoning, no verification.

    Returns the list of search results.
    """
    query = ticket["subject"]
    results = search_kb(query, top_k=top_k)

    content_width = _BOX_WIDTH - 4
    truncated_query = query if len(query) <= content_width - 10 else query[: content_width - 13] + "..."

    lines = [
        _box_top(),
        _box_line("\U0001f50d RAG-ONLY RETRIEVAL (no reasoning, no verification)"),
        _box_mid(),
        _box_empty(),
        _box_line(f'Query: "{truncated_query}"'),
        _box_empty(),
    ]

    for i, result in enumerate(results, 1):
        doc_id = result.get("doc_id", "?")
        score = result.get("similarity_score", 0)
        title = result.get("title", "")
        truncated_title = title if len(title) <= content_width - 4 else title[: content_width - 7] + "..."
        lines.append(_box_line(f"Result {i}: {doc_id} (score: {score})"))
        lines.append(_box_line(f'"{truncated_title}"'))
        lines.append(_box_empty())

    lines.append(_box_mid())
    lines.append(_box_line('\u2139\ufe0f  "This is a lookup, not a decision."'))
    lines.append(_box_bot())

    print("\n".join(lines))
    return results
