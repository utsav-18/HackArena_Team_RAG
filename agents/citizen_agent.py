# agents/citizen_agent.py
# Urban Guardian AI — Citizen Alert Agent
# ─────────────────────────────────────────
# ROLE   : Template-based citizen notification generator — NO Gemini
# INPUT  : assessment + hospital_data + traffic_data (all structured JSON)
# OUTPUT : { "citizen_alert": str, "sms_alert": str, "broadcast_zones": list }
# ─────────────────────────────────────────

from datetime import datetime


# ─── Alert Templates ─────────────────────────────────────────────────────────

TEMPLATES = {
    # Critical severity templates
    "Cardiac Emergency": (
        "🚨 CRITICAL ALERT: A cardiac emergency has been reported near {location}. "
        "Emergency ambulance corridor activated at {junction}. "
        "All vehicles please clear {junction} and use alternate routes immediately. "
        "Ambulance en route to {hospital}."
    ),
    "Road Accident": (
        "⚠️ TRAFFIC ALERT: Road accident reported near {location}. "
        "Emergency corridor activated at {junction}. "
        "Avoid {junction} — use alternate routes. "
        "Emergency services dispatched to {hospital}."
    ),
    "Fire Emergency": (
        "🔥 FIRE ALERT: Fire emergency reported near {location}. "
        "Emergency corridor active at {junction}. "
        "Evacuate the area and clear {junction} for fire brigade and ambulances. "
        "Emergency response coordinated via {hospital}."
    ),
    "Medical Emergency": (
        "🏥 MEDICAL ALERT: Medical emergency reported at {location}. "
        "Emergency corridor activated at {junction}. "
        "Please clear the route for ambulances heading to {hospital}."
    ),
    "General Emergency": (
        "🚦 EMERGENCY ALERT: Emergency situation reported near {location}. "
        "Please follow traffic authorities instructions at {junction}. "
        "Emergency services are responding."
    ),
}

SMS_TEMPLATES = {
    "Critical": "URBAN GUARDIAN: CRITICAL emergency at {location}. Clear {junction} NOW. Ambulance to {hospital}.",
    "High":     "URBAN GUARDIAN: Emergency at {location}. Clear {junction}. Services responding.",
    "Medium":   "URBAN GUARDIAN: Incident at {location}. Minor disruption expected near {junction}.",
    "Low":      "URBAN GUARDIAN: Minor incident near {location}. No major disruption expected.",
}

BROADCAST_ZONES = {
    "A": ["Silk Board Junction", "Hosur Road", "BTM Layout", "Koramangala 5th Block", "Madiwala"],
    "B": ["BTM Layout Water Tank Junction", "JP Nagar", "Bannerghatta Road", "Arekere", "Gottigere"],
    "C": ["Jayadeva Junction", "Bannerghatta Road", "Hulimavu", "Bilekahalli", "Akshayanagar"],
}