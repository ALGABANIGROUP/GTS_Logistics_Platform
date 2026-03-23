# backend/ai/openai_safe_client.py
import os

OPENAI_ENABLED = os.getenv("OPENAI_ENABLED", "0").lower() in ("1", "true", "yes", "on")

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:
    AsyncOpenAI = None  # library not installed or unavailable

def get_openai_client():
    """
    Returns configured AsyncOpenAI or None when disabled/missing.
    Never raises on import-time.
    """
    if not OPENAI_ENABLED:
        return None
    key = os.getenv("OPENAI_API_KEY") or ""
    if not key or AsyncOpenAI is None:
        return None
    return AsyncOpenAI(api_key=key)

# Legacy export; some modules expect a module-level symbol
openai_client = get_openai_client()
