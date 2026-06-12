# agents/traffic_agent.py
# Urban Guardian AI — Traffic Optimization Agent
# ────────────────────────────────────────────────
# ROLE   : Route selection, corridor activation, NodeMCU IoT commands — NO Gemini
# INPUT  : { "severity": str, "type": str, "location": str, "hospital": str }
# OUTPUT : { "route_id": str, "route": list, "junction": str,
#            "corridor_required": bool, "nodemcu_triggered": bool,
#            "nodemcu_status": str }
# ────────────────────────────────────────────────

import os
import requests
from dotenv import load_dotenv

load_dotenv()

NODEMCU_IP = os.getenv("NODEMCU_IP", "192.168.1.100")

# ─── Route & Junction Definitions ────────────────────────────────────────────

ROUTE_MAP = {
    "A": {
        "junction": "Silk Board Junction",
        "waypoints": ["Silk Board Junction", "Hosur Road", "Apollo Hospital"],
        "nodemcu_endpoint": "/emergencyA",
    },
    "B": {
        "junction": "BTM Layout Water Tank Junction",
        "waypoints": ["BTM Layout Water Tank Junction", "Bannerghatta Road", "Narayana Health City"],
        "nodemcu_endpoint": "/emergencyB",
    },
    "C": {
        "junction": "Jayadeva Junction",
        "waypoints": ["Jayadeva Junction", "Bannerghatta Road", "Jayadeva Institute"],
        "nodemcu_endpoint": "/emergencyC",
    },
}

NORMAL_ENDPOINT = "/normal"


# ─── Route Resolver ───────────────────────────────────────────────────────────

def _route_by_location(location: str) -> str | None:
    """Priority 1: Derive route_id from location string."""
    loc = location.lower()
    if any(k in loc for k in ["silk board", "silkboard"]):
        return "A"
    if any(k in loc for k in ["btm", "btm layout", "water tank"]):
        return "B"
    if any(k in loc for k in ["jayadeva"]):
        return "C"
    return None


def _route_by_type(emergency_type: str) -> str:
    """Priority 2: Derive route_id from emergency type (fallback)."""
    t = emergency_type.lower()
    if any(k in t for k in ["fire", "explosion", "blast", "burning"]):
        return "C"
    if any(k in t for k in ["accident", "collision", "crash", "vehicular", "road"]):
        return "B"
    # Cardiac / Medical / Ambulance / Stroke / Trauma → Route A
    return "A"


def _route_by_hospital(hospital: str) -> str | None:
    """Priority 3: Route based on assigned hospital if known."""
    h = hospital.lower()
    if "apollo" in h:
        return "A"
    if "narayana" in h:
        return "B"
    if "jayadeva" in h:
        return "C"
    return None


def resolve_route(location: str, emergency_type: str, hospital: str) -> str:
    """
    Three-tier priority chain:
    1. Location keyword  → most specific
    2. Hospital name     → assigned route
    3. Emergency type    → broad fallback
    """
    route = _route_by_location(location)
    if route:
        return route
    route = _route_by_hospital(hospital)
    if route:
        return route
    return _route_by_type(emergency_type)