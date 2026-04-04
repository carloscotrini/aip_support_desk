"""Mock communication tools for the AIP Support Desk agent."""


def send_email(to: str, subject: str, body: str) -> dict:
    """Draft and display an email response. Does not actually send."""
    width = 50
    border = "═" * width

    print(f"╔{border}╗")
    print(f"║  📧 EMAIL DRAFT (not sent){' ' * (width - 27)}║")
    print(f"╠{border}╣")
    print(f"║  To:      {to:<{width - 12}}║")
    print(f"║  Subject: {subject:<{width - 12}}║")
    print(f"╠{border}╣")

    for line in body.splitlines():
        print(f"║  {line:<{width - 4}}  ║")

    print(f"╚{border}╝")

    return {"status": "draft_created", "to": to, "subject": subject}


def request_info(fields_needed: list[str]) -> dict:
    """Display a formatted clarification request for missing information."""
    width = 50
    border = "═" * width

    print(f"╔{border}╗")
    print(f"║  ❓ INFORMATION REQUEST{' ' * (width - 24)}║")
    print(f"╠{border}╣")
    print(f"║  The agent needs the following info{' ' * (width - 37)}║")
    print(f"║  before proceeding:{' ' * (width - 21)}║")
    print(f"║{' ' * width}║")

    for i, field in enumerate(fields_needed, 1):
        line = f"  {i}. {field}"
        print(f"║{line:<{width}}║")

    print(f"╚{border}╝")

    return {"status": "info_requested", "fields": fields_needed}


SEND_EMAIL_SCHEMA = {
    "name": "send_email",
    "description": "Draft and display an email response to the customer. Does not actually send.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Email body text"},
        },
        "required": ["to", "subject", "body"],
    },
}

REQUEST_INFO_SCHEMA = {
    "name": "request_info",
    "description": "Request additional information from the customer before the agent can proceed.",
    "parameters": {
        "type": "object",
        "properties": {
            "fields_needed": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of fields or pieces of information needed from the customer",
            }
        },
        "required": ["fields_needed"],
    },
}
