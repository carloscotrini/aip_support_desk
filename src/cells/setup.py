# src/cells/setup.py
"""
Setup cell for the AIP Support Desk notebook.

Usage:
    from src.cells.setup import initialize, DEMO_MODE
"""

import json

DEMO_MODE = False


def initialize(demo_mode: bool = True) -> None:
    """Initialize the support desk environment.

    - Sets DEMO_MODE flag
    - Loads pre-computed embeddings
    - Prints a status summary
    """
    global DEMO_MODE
    DEMO_MODE = demo_mode

    # Load embeddings
    from src.data.embeddings import load_embeddings
    embeddings, chunks = load_embeddings()

    # Verify core imports
    from src.data.knowledge_base import KNOWLEDGE_BASE
    from src.data.databases import CUSTOMER_DB, EMPLOYEE_DIRECTORY
    from src.data.tickets import TICKETS
    from src.tools.registry import TOOLS, TOOL_SCHEMAS

    print("=" * 60)
    print("  Meridian Fleet Solutions — AIP Support Desk")
    print("=" * 60)
    print()
    print(f"  Demo mode:        {'ON' if demo_mode else 'OFF (API key required)'}")
    print(f"  KB documents:     {len(KNOWLEDGE_BASE)}")
    print(f"  KB chunks:        {len(chunks)}")
    print(f"  Embedding dims:   {embeddings.shape[1]}")
    print(f"  Customers:        {len(CUSTOMER_DB)}")
    print(f"  Employees:        {len(EMPLOYEE_DIRECTORY)}")
    print(f"  Tickets:          {len(TICKETS)}")
    print(f"  Tools available:  {len(TOOLS)}")
    print()
    print("  Status: READY ✓")
    print("=" * 60)
