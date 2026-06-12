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


# ─── Gemini parser ────────────────────────────────────────────────────────────

def _gemini_parse(text: str) -> dict | None:
    """
    Call Gemini ONCE with the minimal assessment prompt.
    Returns parsed dict on success, None on any failure.
    """
    if not is_available():
        return None

    prompt = EMERGENCY_ASSESSMENT_PROMPT + text

    raw = ask_gemini(prompt)
    if not raw:
        return None

    # Strip markdown code fences if present
    clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    try:
        data = json.loads(clean)
        # Validate required keys
        if all(k in data for k in ("severity", "type", "location")):
            return data
    except (json.JSONDecodeError, ValueError):
        pass

    return None


# ─── Public interface ─────────────────────────────────────────────────────────

class EmergencyAssessmentAgent:
    """
    Agent A — Emergency Assessment Agent
    Sole Gemini-powered agent in the system.
    """

    name = "Emergency Assessment Agent"

    def run(self, emergency_text: str) -> dict:
        """
        Analyze emergency description and return structured assessment.

        Returns:
            {
                "severity": str,
                "type": str,
                "location": str,
                "gemini_used": bool,
                "status": "success" | "fallback"
            }
        """
        # Attempt Gemini (1 call, exactly once)
        result = _gemini_parse(emergency_text)
        gemini_used = True

        if result is None:
            # Graceful fallback to local keyword parser
            result = _local_parse(emergency_text)
            gemini_used = False

        result["gemini_used"] = gemini_used
        result["status"] = "success"
        return result
    

# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = EmergencyAssessmentAgent()
    test = "Critical cardiac patient near Silk Board Junction. Requires immediate ambulance."
    print(agent.run(test))