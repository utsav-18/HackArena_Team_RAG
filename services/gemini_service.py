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