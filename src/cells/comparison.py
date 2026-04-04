# src/cells/comparison.py
"""
Side-by-side comparison view: chatbot response vs. agent trace.
Renders styled HTML in Google Colab via IPython.display.
"""

from __future__ import annotations

import json
from html import escape

from IPython.display import HTML, display

from src.cells.contrast import run_frustrated_chatbot, CHATBOT_DEMO_RESPONSES
from src.agent.loop import run_agent


# ---------------------------------------------------------------------------
# Demo agent responses (pre-scripted for offline/demo mode)
# ---------------------------------------------------------------------------

AGENT_DEMO_RESPONSES: dict[str, list[dict]] = {
    "T1": [
        {
            "reasoning": "Two intents detected: billing dispute + device offline. Starting with billing since it's the primary complaint.",
            "next_tool": "search_kb",
            "tool_args": {"query": "invoice dispute overcharge"},
            "confidence": 0.25,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "KB-003 covers billing disputes. Need to check customer account status and tier for specific policy.",
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1001"},
            "confidence": 0.45,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Customer is on Premium tier. Now addressing the second intent: GPS device offline.",
            "next_tool": "search_kb",
            "tool_args": {"query": "GPS device offline troubleshooting"},
            "confidence": 0.60,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Have billing policy and device troubleshooting info. Drafting a comprehensive response addressing both issues with tier-specific details.",
            "next_tool": "draft_email",
            "tool_args": {"to": "CUST-1001", "subject": "Re: Invoice Overcharge & Device Offline", "body": "Detailed resolution addressing both issues"},
            "confidence": 0.85,
            "resolution_status": "RESOLVED",
        },
    ],
    "T2": [
        {
            "reasoning": "Device-specific issue reported. Need to identify the exact device model and known issues.",
            "next_tool": "search_kb",
            "tool_args": {"query": "GPS tracker offline intermittent"},
            "confidence": 0.20,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Found relevant KB article. Need to verify customer's device model and firmware version.",
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1002"},
            "confidence": 0.50,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Device is running outdated firmware with a known bug. Drafting response with specific fix.",
            "next_tool": "draft_email",
            "tool_args": {"to": "CUST-1002", "subject": "Re: GPS Device Issue - Firmware Update Required", "body": "Specific firmware update instructions"},
            "confidence": 0.82,
            "resolution_status": "RESOLVED",
        },
    ],
    "T3": [
        {
            "reasoning": "Complex ticket with 3 intents: billing, device, and contract question. Addressing each systematically.",
            "next_tool": "search_kb",
            "tool_args": {"query": "invoice dispute"},
            "confidence": 0.15,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Need to check customer account for all three issues.",
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1003"},
            "confidence": 0.35,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Account is SUSPENDED. This changes everything — root cause is billing. Replanning.",
            "next_tool": "search_kb",
            "tool_args": {"query": "suspended account reinstatement policy"},
            "confidence": 0.30,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Have full picture now. Account suspension caused device issues. Drafting comprehensive response for all 3 intents.",
            "next_tool": "draft_email",
            "tool_args": {"to": "CUST-1003", "subject": "Re: Multiple Issues - Account Status Update", "body": "Comprehensive resolution for all three issues"},
            "confidence": 0.80,
            "resolution_status": "RESOLVED",
        },
    ],
    "T4": [
        {
            "reasoning": "Customer asking about cancellation. Need to find the correct cancellation policy, not onboarding.",
            "next_tool": "search_kb",
            "tool_args": {"query": "contract cancellation policy"},
            "confidence": 0.25,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Found cancellation policy. Need to check customer's contract terms and early termination fees.",
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1004"},
            "confidence": 0.55,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "High-value customer threatening cancellation. This exceeds front-line authority — escalating to retention team.",
            "next_tool": "escalate",
            "tool_args": {"to": "retention_team", "summary": "High-value customer requesting cancellation, needs retention offer"},
            "confidence": 0.85,
            "resolution_status": "RESOLVED",
        },
    ],
    "T5": [
        {
            "reasoning": "Urgent executive complaint from CFO. Need to understand the full scope immediately.",
            "next_tool": "query_customer_db",
            "tool_args": {"customer_id": "CUST-1005"},
            "confidence": 0.10,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "Enterprise account with significant revenue. Need to pull billing history and recent issues.",
            "next_tool": "search_kb",
            "tool_args": {"query": "enterprise billing escalation executive complaint"},
            "confidence": 0.30,
            "resolution_status": "INVESTIGATING",
        },
        {
            "reasoning": "CFO involvement and billing amount exceed front-line authority. Must escalate to senior management with full context.",
            "next_tool": "escalate",
            "tool_args": {"to": "senior_management", "summary": "CFO complaint — enterprise account, urgent billing dispute, revenue at risk"},
            "confidence": 0.40,
            "resolution_status": "ESCALATING",
        },
        {
            "reasoning": "Escalation filed. Sending acknowledgement email to CFO confirming we've prioritized this.",
            "next_tool": "draft_email",
            "tool_args": {"to": "CUST-1005", "subject": "Re: Urgent - Executive Escalation Acknowledged", "body": "Priority acknowledgement with escalation reference"},
            "confidence": 0.82,
            "resolution_status": "RESOLVED",
        },
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _confidence_badge(confidence: float) -> str:
    """Return an HTML badge colored by confidence level."""
    if confidence >= 0.8:
        color = "#2e7d32"
        bg = "#c8e6c9"
        label = "HIGH CONFIDENCE"
    elif confidence >= 0.5:
        color = "#f57f17"
        bg = "#fff9c4"
        label = "MEDIUM CONFIDENCE"
    else:
        color = "#c62828"
        bg = "#ffcdd2"
        label = "LOW CONFIDENCE"

    return (
        f'<span style="display:inline-block;padding:4px 12px;'
        f"border-radius:4px;font-weight:bold;font-size:14px;"
        f"color:{color};background:{bg};border:2px solid {color};"
        f'">{label} ({int(confidence * 100)}%)</span>'
    )


def _format_agent_trace(agent_state: dict) -> str:
    """Convert agent_state['steps_taken'] into an HTML-formatted trace."""
    steps = agent_state.get("steps_taken", [])
    if not steps:
        return "<p><em>No steps recorded.</em></p>"

    lines: list[str] = []

    for i, step in enumerate(steps, 1):
        phase_num = step.get("phase", i)
        tool = step.get("tool", "unknown")
        inputs = step.get("inputs", {})
        outputs = step.get("outputs", {})
        reasoning = step.get("reasoning", "")

        # PLAN
        lines.append(
            f'<div style="margin-bottom:8px;">'
            f'<strong style="color:#1565c0;">Step {phase_num} [PLAN]:</strong> '
            f'"{escape(reasoning)}"'
            f"</div>"
        )

        # ACT
        args_str = ", ".join(
            f'{k}="{escape(str(v))}"' if isinstance(v, str) else f"{k}={escape(str(v))}"
            for k, v in inputs.items()
        )
        result_summary = json.dumps(outputs, default=str)
        if len(result_summary) > 120:
            result_summary = result_summary[:120] + "..."

        lines.append(
            f'<div style="margin-bottom:4px;padding-left:20px;">'
            f'<strong style="color:#4527a0;">Step {phase_num} [ACT]:</strong> '
            f"<code>{escape(tool)}({escape(args_str)})</code>"
            f"</div>"
        )

        # OBSERVE
        lines.append(
            f'<div style="margin-bottom:4px;padding-left:20px;color:#555;">'
            f"<strong>[OBSERVE]:</strong> {escape(result_summary)}"
            f"</div>"
        )

        # REFLECT
        reflect_note = ""
        if "replan" in reasoning.lower() or "contradict" in reasoning.lower():
            reflect_note = " Replanning."
        lines.append(
            f'<div style="margin-bottom:12px;padding-left:20px;'
            f'border-bottom:1px dashed #ccc;padding-bottom:8px;">'
            f'<strong style="color:#2e7d32;">[REFLECT]:</strong> '
            f"Processing observation.{reflect_note}"
            f"</div>"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main comparison view
# ---------------------------------------------------------------------------

def run_comparison(
    ticket: dict,
    chatbot_response: str | None = None,
    agent_state: dict | None = None,
) -> None:
    """Render a split-screen HTML view comparing chatbot vs. agent."""

    # Fill in defaults if not provided
    if chatbot_response is None:
        chatbot_response = run_frustrated_chatbot(
            ticket,
            demo_response=CHATBOT_DEMO_RESPONSES.get(ticket["ticket_id"]),
        )

    if agent_state is None:
        demo = AGENT_DEMO_RESPONSES.get(ticket["ticket_id"])
        agent_state = run_agent(
            ticket,
            demo_responses=list(demo) if demo else None,
        )

    confidence = agent_state.get("confidence", 0.0)
    agent_trace_html = _format_agent_trace(agent_state)
    badge_html = _confidence_badge(confidence)

    html = f"""
    <div style="display:flex;flex-wrap:wrap;gap:16px;font-family:Arial,Helvetica,sans-serif;max-width:1200px;margin:0 auto;">

      <!-- LEFT: Chatbot -->
      <div style="flex:1 1 45%;min-width:300px;border:3px solid #c62828;border-radius:8px;
                  background:#fff5f5;padding:20px;">
        <div style="font-size:20px;font-weight:bold;color:#c62828;margin-bottom:4px;">
          &#129302; Chatbot Response
        </div>
        <div style="font-size:13px;color:#888;margin-bottom:16px;font-style:italic;">
          No tools, no reasoning loop
        </div>
        <div style="font-size:15px;line-height:1.6;color:#333;white-space:pre-wrap;">
{escape(chatbot_response)}
        </div>
      </div>

      <!-- RIGHT: Agent -->
      <div style="flex:1 1 45%;min-width:300px;border:3px solid #2e7d32;border-radius:8px;
                  background:#f1f8e9;padding:20px;">
        <div style="font-size:20px;font-weight:bold;color:#2e7d32;margin-bottom:4px;">
          &#9881;&#129504; Agent Response
        </div>
        <div style="font-size:13px;color:#888;margin-bottom:16px;font-style:italic;">
          PLAN &rarr; ACT &rarr; OBSERVE &rarr; REFLECT
        </div>
        <div style="font-family:monospace;font-size:13px;line-height:1.5;color:#222;">
{agent_trace_html}
        </div>
        <div style="margin-top:16px;text-align:right;">
          {badge_html}
        </div>
      </div>

    </div>

    <!-- Caption -->
    <div style="text-align:center;margin-top:20px;font-size:16px;color:#555;font-style:italic;">
      &ldquo;The chatbot responded. The agent <strong>worked</strong>.&rdquo;
    </div>
    """

    display(HTML(html))
