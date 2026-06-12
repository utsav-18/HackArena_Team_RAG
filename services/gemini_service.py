# services/gemini_service.py
# Urban Guardian AI — Gemini API Service
# Uses the current google-genai SDK (google.genai).
# Single responsibility: Call Gemini once and return raw text.
# Only the Emergency Assessment Agent uses this service.
# All other agents are rule-based and NEVER call this service.

import os
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
_client  = None

if _api_key:
    try:
        from google import genai
        _client = genai.Client(api_key=_api_key)
    except Exception as _e:
        print(f"[GeminiService] Failed to initialise google.genai client: {_e}")
        _client = None
def ask_gemini(prompt: str) -> str | None:
    """
    Call Gemini 2.5 Flash with the given prompt and return the raw response text.
    Returns None on failure so the caller can handle fallback logic.
    This function is intentionally simple — it does ONE thing: call Gemini once.
    """
    if not _client:
        return None
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[GeminiService] Error: {e}")
        return None

def is_available() -> bool:
    """Returns True if the Gemini client is initialised and ready."""
    return _client is not None
