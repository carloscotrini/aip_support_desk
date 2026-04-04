"""Setup cell — dependency check, API key config, embedding loading."""

import getpass

DEMO_MODE = True  # Default: pre-scripted responses, no API key needed

DEPENDENCIES = [
    "anthropic",
    "sentence-transformers",
    "scikit-learn",
]


def install_dependencies() -> None:
    """Verify core imports are available; point to requirements.txt if not."""
    missing = []
    for dep in DEPENDENCIES:
        module_name = dep.replace("-", "_")
        # scikit-learn imports as sklearn
        if module_name == "scikit_learn":
            module_name = "sklearn"
        try:
            __import__(module_name)
        except ImportError:
            missing.append(dep)

    if missing:
        print(f"[SETUP] ⚠ Missing packages: {', '.join(missing)}")
        print("  Install into your environment first:")
        print("    pip install -r requirements.txt")
    else:
        print("[SETUP] All dependencies available.")


def configure_api_key(demo_mode: bool = True) -> str | None:
    """Prompt for API key in live mode; skip in demo mode."""
    if demo_mode:
        print("[SETUP] DEMO_MODE=True — using pre-scripted responses (no API key needed)")
        return None

    print("[SETUP] Live mode — enter your Anthropic API key:")
    key = getpass.getpass("API key: ")
    return key


def initialize(demo_mode: bool = True) -> dict:
    """
    Run all setup steps and return a config dict.

    Returns:
        {
            "demo_mode": bool,
            "api_key": str | None,
            "embeddings_loaded": bool,
            "tools_available": list[str],
        }
    """
    global DEMO_MODE
    DEMO_MODE = demo_mode

    # 1. API key
    api_key = configure_api_key(demo_mode)

    # 2. Load embeddings
    embeddings_loaded = False
    num_chunks = 0
    num_docs = 0
    try:
        from src.data.embeddings import load_embeddings
        _embeddings, chunks = load_embeddings()
        embeddings_loaded = True
        num_chunks = len(chunks)
        num_docs = len({c["doc_id"] for c in chunks})
    except Exception as e:
        print(f"[SETUP] ⚠ Could not load embeddings: {e}")

    # 3. Verify tool modules
    tools_available: list[str] = []
    try:
        from src.tools.registry import get_tool_names
        tools_available = get_tool_names()
    except Exception as e:
        print(f"[SETUP] ⚠ Could not load tools: {e}")

    # 4. Print summary
    mode_str = "DEMO (pre-scripted responses)" if demo_mode else "LIVE (Anthropic API)"
    emb_str = f"Loaded ({num_chunks} chunks from {num_docs} KB documents)" if embeddings_loaded else "Not loaded"

    w = 58
    print()
    print(f"╔{'═' * w}╗")
    print(f"║  {'✅ SETUP COMPLETE':<{w - 2}}║")
    print(f"╠{'═' * w}╣")
    print(f"║  {'Mode:':<14}{mode_str:<{w - 16}}║")
    print(f"║  {'Embeddings:':<14}{emb_str:<{w - 16}}║")
    print(f"║  {'Tools:':<14}{len(tools_available)} available{' ' * (w - 16 - len(str(len(tools_available))) - 10)}║")
    for name in tools_available:
        print(f"║    • {name:<{w - 6}}║")
    print(f"╠{'═' * w}╣")
    print(f"║  {'Ready! Change ACTIVE_TICKET and run the cells below.':<{w - 2}}║")
    print(f"╚{'═' * w}╝")

    return {
        "demo_mode": demo_mode,
        "api_key": api_key,
        "embeddings_loaded": embeddings_loaded,
        "tools_available": tools_available,
    }
