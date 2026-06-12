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


# ─── Public interface ─────────────────────────────────────────────────────────

class CitizenAlertAgent:
    """
    Agent D — Citizen Alert Agent
    Pure template engine. Zero AI/Gemini calls.
    """

    name = "Citizen Alert Agent"

    def run(self, assessment: dict, hospital_data: dict, traffic_data: dict) -> dict:
        """
        Generate citizen notifications from structured agent data.

        Args:
            assessment   : EmergencyAssessmentAgent output
            hospital_data: HospitalCoordinationAgent output
            traffic_data : TrafficOptimizationAgent output

        Returns:
            {
                "citizen_alert": str,       # Main dashboard notification
                "sms_alert": str,           # Short SMS-style alert
                "broadcast_zones": list,    # Areas that receive the alert
                "timestamp": str,
                "status": "success"
            }
        """
        location = assessment.get("location", "Unknown")
        severity = assessment.get("severity", "Low")
        emergency_type = assessment.get("type", "General Emergency")
        hospital = hospital_data.get("hospital", "Nearest Hospital")
        junction = traffic_data.get("junction", "Emergency Junction")
        route_id = traffic_data.get("route_id", "A")
        corridor_required = traffic_data.get("corridor_required", False)

        # Select template by emergency type (use General as fallback)
        template = TEMPLATES.get(emergency_type, TEMPLATES["General Emergency"])

        # Fill in the template
        citizen_alert = template.format(
            location=location,
            junction=junction,
            hospital=hospital,
        )

        # Add corridor status suffix
        if not corridor_required:
            citizen_alert = (
                f"ℹ️ ADVISORY: Non-critical incident reported near {location}. "
                f"No traffic disruptions expected. Emergency services are aware."
            )

        # Short SMS alert
        sms_template = SMS_TEMPLATES.get(severity, SMS_TEMPLATES["Low"])
        sms_alert = sms_template.format(
            location=location,
            junction=junction,
            hospital=hospital,
        )

        # Affected broadcast zones
        zones = BROADCAST_ZONES.get(route_id, ["Bengaluru"])

        timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")

        return {
            "citizen_alert": citizen_alert,
            "sms_alert": sms_alert,
            "broadcast_zones": zones,
            "timestamp": timestamp,
            "status": "success",
        }