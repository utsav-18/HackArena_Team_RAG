# agents/hospital_agent.py
# Urban Guardian AI — Hospital Coordination Agent
# ─────────────────────────────────────────────────
# ROLE   : Rule-based hospital selector — NO Gemini calls
# INPUT  : { "severity": str, "type": str, "location": str }
# OUTPUT : { "hospital": str, "hospital_contact": str, "eta_minutes": int }
# LOGIC  : Location-first mapping → Emergency-type fallback → Default
# ─────────────────────────────────────────────────

# ─── Hospital Database ────────────────────────────────────────────────────────
# Covers three primary Bengaluru emergency corridors and surrounding areas.

HOSPITAL_DB = {
    # ── Route A Corridor — Silk Board / Medical emergencies ───────────────────
    "Apollo Hospital": {
        "contact": "+91-80-2941-4444",
        "eta_minutes": 8,
        "specialties": ["cardiac", "trauma", "medical", "stroke", "general"],
        "zones": ["silk board", "silkboard", "koramangala", "hsr layout", "hsr",
                  "btm layout", "btm", "marathahalli"],
    },
    # ── Route B Corridor — BTM / Accident / Road Trauma ───────────────────────
    "Narayana Health City": {
        "contact": "+91-80-2178-5000",
        "eta_minutes": 10,
        "specialties": ["accident", "road accident", "trauma", "orthopedic", "surgery"],
        "zones": ["btm layout", "btm", "water tank", "bannerghatta", "electronic city",
                  "jp nagar"],
    },
    # ── Route C Corridor — Jayadeva / Cardiac / Fire ──────────────────────────
    "Jayadeva Institute of Cardiovascular Sciences": {
        "contact": "+91-80-2665-5000",
        "eta_minutes": 7,
        "specialties": ["cardiac", "cardiac emergency", "heart attack", "cardiovascular"],
        "zones": ["jayadeva", "jayadeva junction", "bannerghatta road"],
    },
    # ── Fire / Explosion ──────────────────────────────────────────────────────
    "Victoria Hospital": {
        "contact": "+91-80-2670-1150",
        "eta_minutes": 12,
        "specialties": ["fire", "fire emergency", "explosion", "burns", "blast"],
        "zones": ["city market", "shivajinagar", "majestic"],
    },
    # ── General / Unknown fallback ────────────────────────────────────────────
    "Manipal Hospital": {
        "contact": "+91-80-2502-4444",
        "eta_minutes": 15,
        "specialties": ["general", "general emergency"],
        "zones": ["whitefield", "old airport road"],
    },
}

DEFAULT_HOSPITAL = "Apollo Hospital"


# ─── Selector Logic ───────────────────────────────────────────────────────────

def _match_by_location(location: str) -> str | None:
    """
    Priority 1: Match hospital by geographic zone keyword in location string.
    Returns hospital name or None.
    """
    loc_lower = location.lower()
    for hospital_name, info in HOSPITAL_DB.items():
        if any(zone in loc_lower for zone in info["zones"]):
            return hospital_name
    return None


def _match_by_type(emergency_type: str) -> str | None:
    """
    Priority 2: Match hospital by emergency type specialty.
    Returns hospital name or None.
    """
    type_lower = emergency_type.lower()
    for hospital_name, info in HOSPITAL_DB.items():
        if any(spec in type_lower for spec in info["specialties"]):
            return hospital_name
    return None



# ─── Public interface ─────────────────────────────────────────────────────────

class HospitalCoordinationAgent:
    """
    Agent B — Hospital Coordination Agent
    Pure rule-based. Zero AI/Gemini calls.
    """

    name = "Hospital Coordination Agent"

    def run(self, assessment: dict) -> dict:
        """
        Select best hospital based on emergency assessment.

        Args:
            assessment: Output from EmergencyAssessmentAgent
                        { "severity": str, "type": str, "location": str }

        Returns:
            {
                "hospital": str,
                "hospital_contact": str,
                "eta_minutes": int,
                "selection_reason": str,
                "status": "success"
            }
        """
        location = assessment.get("location", "Unknown")
        emergency_type = assessment.get("type", "General Emergency")

        # Location-first, type-fallback matching
        hospital_name = _match_by_location(location)
        reason = "location-based match"

        if not hospital_name:
            hospital_name = _match_by_type(emergency_type)
            reason = "emergency-type match"

        if not hospital_name:
            hospital_name = DEFAULT_HOSPITAL
            reason = "default fallback"

        info = HOSPITAL_DB[hospital_name]

        return {
            "hospital": hospital_name,
            "hospital_contact": info["contact"],
            "eta_minutes": info["eta_minutes"],
            "selection_reason": reason,
            "status": "success",
        }


# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = HospitalCoordinationAgent()
    test_assessment = {
        "severity": "Critical",
        "type": "Cardiac Emergency",
        "location": "Silk Board Junction",
    }
    print(agent.run(test_assessment))