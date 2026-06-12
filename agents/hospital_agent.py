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