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


# ─── Corridor Activation ──────────────────────────────────────────────────────

def _requires_corridor(severity: str) -> bool:
    """Only Critical and High emergencies activate the corridor."""
    return severity.lower() in ("critical", "high")


def _trigger_nodemcu(endpoint: str) -> tuple[bool, str]:
    """
    Send HTTP GET to NodeMCU ESP8266/NodeMCU.
    Returns (success: bool, message: str).
    """
    try:
        url = f"http://{NODEMCU_IP}{endpoint}"
        r = requests.get(url, timeout=2)
        if r.status_code == 200:
            return True, f"NodeMCU responded OK ({url})"
        return False, f"NodeMCU returned HTTP {r.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "NodeMCU offline / unreachable"
    except requests.exceptions.Timeout:
        return False, "NodeMCU connection timed out"
    except Exception as e:
        return False, f"NodeMCU error: {str(e)}"


# ─── Public interface ─────────────────────────────────────────────────────────

class TrafficOptimizationAgent:
    """
    Agent C — Traffic Optimization Agent
    Pure decision logic. Zero AI/Gemini calls.
    Triggers physical IoT NodeMCU traffic control.
    """

    name = "Traffic Optimization Agent"

    def run(self, assessment: dict, hospital_data: dict) -> dict:
        """
        Determine route and activate emergency traffic corridor via NodeMCU.

        Args:
            assessment   : EmergencyAssessmentAgent output
            hospital_data: HospitalCoordinationAgent output

        Returns:
            {
                "route_id": str,          # "A", "B", or "C"
                "route": list[str],       # Waypoints from incident to hospital
                "junction": str,          # Active Bengaluru junction name
                "corridor_required": bool,
                "nodemcu_triggered": bool,
                "nodemcu_status": str,
                "status": "success"
            }
        """
        location = assessment.get("location", "Unknown")
        emergency_type = assessment.get("type", "General Emergency")
        severity = assessment.get("severity", "Low")
        hospital = hospital_data.get("hospital", "")

        # Resolve route (3-tier priority)
        route_id = resolve_route(location, emergency_type, hospital)
        route_info = ROUTE_MAP[route_id]

        corridor_required = _requires_corridor(severity)

        # Build route waypoints: start at incident location → junction → hospital
        route_waypoints = [location] + route_info["waypoints"]
        # Deduplicate consecutive duplicates
        seen = []
        for wp in route_waypoints:
            if not seen or seen[-1].lower() != wp.lower():
                seen.append(wp)
        route_waypoints = seen

        # NodeMCU control
        nodemcu_triggered = False
        nodemcu_status = "Corridor not required for this severity level."

        if corridor_required:
            success, msg = _trigger_nodemcu(route_info["nodemcu_endpoint"])
            nodemcu_triggered = success
            nodemcu_status = msg
        else:
            # Return to normal mode
            _trigger_nodemcu(NORMAL_ENDPOINT)
            nodemcu_status = "Normal traffic mode maintained."

        return {
            "route_id": route_id,
            "route": route_waypoints,
            "junction": route_info["junction"],
            "corridor_required": corridor_required,
            "nodemcu_triggered": nodemcu_triggered,
            "nodemcu_status": nodemcu_status,
            "status": "success",
        }
