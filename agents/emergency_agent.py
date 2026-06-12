# agents/emergency_agent.py
# Urban Guardian AI — Emergency Assessment Agent
# ─────────────────────────────────────────────
# ROLE       : The ONLY agent that calls Gemini. Called exactly ONCE per request.
# INPUT      : Raw natural-language emergency description (str)
# OUTPUT     : { "severity": str, "type": str, "location": str }
# FALLBACK   : Local keyword-based parser (no Gemini, no external calls)
# ─────────────────────────────────────────────

import json
import re
import sys
import os

# Ensure parent directory is on path when running standalone
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gemini_service import ask_gemini, is_available
from utils.prompts import EMERGENCY_ASSESSMENT_PROMPT


# ─── Local keyword fallback (no Gemini) ───────────────────────────────────────

def _local_severity(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["cardiac", "heart attack", "unconscious", "stroke", "life-threatening", "critical"]):
        return "Critical"
    if any(k in t for k in ["accident", "collision", "fire", "explosion", "serious", "severe"]):
        return "High"
    if any(k in t for k in ["fracture", "breathing", "fever", "injury"]):
        return "Medium"
    return "Low"


def _local_type(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["cardiac", "heart", "chest pain"]):
        return "Cardiac Emergency"
    if any(k in t for k in ["accident", "collision", "crash", "vehicle"]):
        return "Road Accident"
    if any(k in t for k in ["fire", "explosion", "blast", "burning"]):
        return "Fire Emergency"
    if any(k in t for k in ["ambulance", "stroke", "trauma", "medical"]):
        return "Medical Emergency"
    return "General Emergency"


def _local_location(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["silk board", "silkboard"]):
        return "Silk Board Junction"
    if any(k in t for k in ["btm layout", "btm", "water tank"]):
        return "BTM Layout Water Tank Junction"
    if any(k in t for k in ["jayadeva"]):
        return "Jayadeva Junction"
    if any(k in t for k in ["koramangala"]):
        return "Koramangala"
    if any(k in t for k in ["hsr layout", "hsr"]):
        return "HSR Layout"
    if any(k in t for k in ["marathahalli"]):
        return "Marathahalli"
    if any(k in t for k in ["whitefield"]):
        return "Whitefield"
    if any(k in t for k in ["electronic city"]):
        return "Electronic City"
    if any(k in t for k in ["bannerghatta"]):
        return "Bannerghatta Road"
    return "Unknown"


def _local_parse(text: str) -> dict:
    """Rule-based emergency parser — zero Gemini calls."""
    return {
        "severity": _local_severity(text),
        "type": _local_type(text),
        "location": _local_location(text),
    }