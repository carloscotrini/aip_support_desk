"""End-to-end smoke tests for the AIP Support Desk pipeline."""

from src.data.tickets import TICKETS
from src.agent.demo_responses import get_demo_responses, DEMO_RESPONSES
from src.agent.loop import run_agent
from src.cells.contrast import run_frustrated_chatbot, CHATBOT_DEMO_RESPONSES, run_rag_only
from src.cells.reentry import resume_agent, NEXT_MORNING_MESSAGE, REENTRY_DEMO_RESPONSES
from src.tools.registry import TOOLS, dispatch_tool


def test_all_tickets_demo_mode():
    """Run all 5 tickets through the agent loop in demo mode."""
    for ticket_id in ["T1", "T2", "T3", "T4", "T5"]:
        ticket = TICKETS[ticket_id]
        responses = get_demo_responses(ticket_id)
        state = run_agent(ticket, demo_responses=responses)
        assert state["status"] == "RESOLVED", f"{ticket_id} did not resolve"
        assert len(state["steps_taken"]) > 0, f"{ticket_id} took no steps"


def test_chatbot_contrast():
    """Verify chatbot demo responses exist for all tickets."""
    for ticket_id in ["T1", "T2", "T3", "T4", "T5"]:
        assert ticket_id in CHATBOT_DEMO_RESPONSES, f"Missing chatbot response for {ticket_id}"
        ticket = TICKETS[ticket_id]
        response = run_frustrated_chatbot(
            ticket,
            demo_response=CHATBOT_DEMO_RESPONSES[ticket_id],
        )
        assert isinstance(response, str)
        assert len(response) > 0


def test_rag_only():
    """Verify search_kb returns results for each ticket subject."""
    for ticket_id in ["T1", "T2", "T3", "T4", "T5"]:
        ticket = TICKETS[ticket_id]
        results = run_rag_only(ticket)
        assert isinstance(results, list)
        assert len(results) > 0, f"No RAG results for {ticket_id}"


def test_reentry():
    """Verify stateful re-entry works with demo responses."""
    ticket = TICKETS["T3"]
    responses = get_demo_responses("T3")
    state = run_agent(ticket, demo_responses=responses)
    assert state["status"] == "RESOLVED"

    steps_before = len(state["steps_taken"])
    reentry_responses = [dict(r) for r in REENTRY_DEMO_RESPONSES]
    updated = resume_agent(
        state,
        NEXT_MORNING_MESSAGE["body"],
        demo_responses=reentry_responses,
    )
    assert updated["status"] == "RESOLVED"
    assert len(updated["steps_taken"]) > steps_before


def test_tool_dispatch():
    """Verify all 7 tools are dispatchable."""
    expected_tools = [
        "search_kb",
        "query_customer_db",
        "send_email",
        "escalate",
        "request_info",
        "check_sla_status",
        "check_open_cases",
    ]
    for tool_name in expected_tools:
        assert tool_name in TOOLS, f"Tool {tool_name} not in registry"

    # Dispatch a known tool to verify the pipeline works
    result = dispatch_tool("search_kb", query="mileage report")
    assert isinstance(result, (dict, list))
    assert "error" not in result if isinstance(result, dict) else True
