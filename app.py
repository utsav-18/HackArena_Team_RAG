# app.py
# Urban Guardian AI - HackArena Edition
from backup_ai import backup_analysis
from typing import Optional
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import requests
import folium
from streamlit_folium import st_folium
# =========================================================
# CONFIG
# =========================================================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NODEMCU_IP = os.getenv("NODEMCU_IP")
st.set_page_config(
    page_title="Urban Guardian AI",
    page_icon="🚑",
    layout="wide"
)
# =========================================================
# ROUTE JUNCTION MAPPING
# Maps route_id codes to real Bengaluru junction names.
# =========================================================
ROUTE_JUNCTION = {
    "A": "Silk Board Junction",
    "B": "BTM Layout Water Tank Junction",
    "C": "Jayadeva Junction"
}
# =========================================================
# FUTURISTIC CSS
# =========================================================
st.markdown("""
<style>
.stApp{
    background:
    linear-gradient(
        135deg,
        #020617,
        #0f172a,
        #020617
    );
}
/* Hide Streamlit Branding */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
/* HERO */
.hero{
    text-align:center;
    padding:30px;
    border-radius:25px;
    background:
    linear-gradient(
        135deg,
        rgba(0,255,255,0.12),
        rgba(37,99,235,0.12)
    );
    border:
    1px solid rgba(0,255,255,0.25);
    box-shadow:
    0px 0px 35px rgba(0,255,255,0.15);
}
.hero-title{
    font-size:58px;
    font-weight:800;
    background:
    linear-gradient(
        90deg,
        #00ffff,
        #38bdf8,
        #60a5fa
    );
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.hero-sub{
    color:#94a3b8;
    font-size:18px;
}
/* METRICS */
[data-testid="metric-container"] {
    background:
    rgba(15,23,42,0.8);
    border:
    1px solid rgba(0,255,255,0.15);
    border-radius:20px;
    padding:15px;
    box-shadow:
    0px 0px 20px rgba(0,255,255,0.08);
}
[data-testid="metric-container"]:hover {
    transform:translateY(-5px);
    transition:0.3s ease;
    box-shadow:
    0px 0px 30px rgba(0,255,255,0.3);
}
/* BUTTON */
.stButton > button {
    width:100%;
    height:55px;
    border:none;
    border-radius:15px;
    color:white;
    font-size:18px;
    font-weight:bold;
    background:
    linear-gradient(
        90deg,
        #06b6d4,
        #2563eb
    );
    box-shadow:
    0px 0px 25px rgba(37,99,235,0.35);
}
.stButton > button:hover {
    transform:scale(1.02);
    transition:0.3s;
    box-shadow:
    0px 0px 35px rgba(0,255,255,0.5);
}
/* TEXT AREA */
textarea {
    background:
    rgba(15,23,42,0.8) !important;
    color:white !important;
    border:
    1px solid rgba(0,255,255,0.2) !important;
    border-radius:15px !important;
}
/* GLASS CARD */
.glass{
    background:
    rgba(255,255,255,0.04);
    backdrop-filter:
    blur(15px);
    border:
    1px solid rgba(255,255,255,0.08);
    border-radius:20px;
    padding:20px;
}
/* GLOW */
@keyframes pulse {
    0%{
        box-shadow:
        0px 0px 15px rgba(0,255,255,0.1);
    }
    50%{
        box-shadow:
        0px 0px 35px rgba(0,255,255,0.35);
    }
    100%{
        box-shadow:
        0px 0px 15px rgba(0,255,255,0.1);
    }
}
.glow{
    animation:pulse 3s infinite;
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# GEMINI
# =========================================================
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
# =========================================================
# LOCATION-BASED ROUTE OVERRIDE
# Determines route_id from the detected location string.
# Runs after Gemini parse to ensure the correct Bengaluru
# junction corridor is activated.
#
# Silk Board Junction          → Route A
# BTM Layout Water Tank Jn.    → Route B
# Jayadeva Junction            → Route C
# =========================================================
def determine_route_id_by_location(location: str) -> Optional[str]:
    """
    Derive route_id from the location field returned by Gemini.
    Returns A, B, or C if a known Bengaluru junction is detected.
    Returns None if the location does not match any known junction,
    allowing the emergency-type fallback to take over.
    Compatible with Python 3.8+.
    """
    loc = location.lower()
    # Route A — Silk Board Junction variants
    if any(x in loc for x in [
        "silk board",
        "silkboard",
        "silk board junction"
    ]):
        return "A"
    # Route B — BTM Layout Water Tank Junction variants
    if any(x in loc for x in [
        "btm",
        "btm layout",
        "water tank"
    ]):
        return "B"
    # Route C — Jayadeva Junction variants
    if any(x in loc for x in [
        "jayadeva",
        "jayadeva junction",
        "jayadeva hospital"
    ]):
        return "C"
    return None  # No location match — defer to emergency-type logic
# =========================================================
# EMERGENCY-TYPE ROUTE OVERRIDE
# Determines route_id from emergency type keywords.
# Used as the secondary fallback when location is not matched.
# =========================================================
def determine_route_id_by_type(emergency_type: str) -> str:
    """
    Derive the correct route_id from the emergency type string.
    Route A (Silk Board Junction)               → Medical / Cardiac / Ambulance
    Route B (BTM Layout Water Tank Junction)    → Road Accident / Collision / Crash
    Route C (Jayadeva Junction)                 → Fire / Explosion / Building Fire
    """
    t = emergency_type.lower()
    # Route C — Fire emergencies (check before generic keywords)
    if any(k in t for k in ["fire", "explosion", "blast", "inferno", "burning"]):
        return "C"
    # Route B — Road accident / collision
    if any(k in t for k in ["accident", "collision", "crash", "vehicular", "highway", "road"]):
        return "B"
    # Route A — Medical / cardiac / ambulance (default for medical)
    if any(k in t for k in [
        "cardiac", "heart", "medical", "ambulance",
        "stroke", "trauma", "injury", "patient", "emergency"
    ]):
        return "A"
    # Default fallback — treat unknown as medical (Silk Board Junction)
    return "A"
# =========================================================
# COMBINED ROUTE RESOLVER
# Location takes priority; emergency type is the fallback.
# =========================================================
def resolve_route_id(location: str, emergency_type: str) -> str:
    """
    Resolve final route_id using a two-step priority chain:
    1. Location-based detection  (Silk Board / BTM / Jayadeva)
    2. Emergency-type keywords   (cardiac / accident / fire)
    """
    route = determine_route_id_by_location(location)
    if route:
        return route
    return determine_route_id_by_type(emergency_type)
# =========================================================
# FALLBACK
# Returns a safe static response when all AI fails.
# =========================================================
def fallback_response() -> dict:
    """Returns a hardcoded safe fallback response dict."""
    return {
        "severity": "Critical",
        "type": "Cardiac Emergency",
        "location": "Silk Board Junction",
        "hospital": "Apollo Hospital",
        "route": [
            "Silk Board Junction",
            "BTM Layout",
            "Apollo Hospital"
        ],
        "route_id": "A",
        "corridor_required": True,
        "citizen_alert": "Emergency ambulance approaching Silk Board Junction. Please use alternate routes."
    }
# =========================================================
# ANALYZE EMERGENCY
# Primary AI function. Calls Gemini, parses response,
# overrides route_id by location then type, falls back
# gracefully on any error.
# =========================================================
def analyze_emergency(text: str) -> dict:
    """
    Analyze an emergency description using Gemini AI.
    Steps:
    1. Build structured prompt requesting JSON output.
       Prompt includes Bengaluru junction → route_id mapping.
    2. Call Gemini API.
    3. Parse JSON response safely.
    4. Override route_id using location-first, type-second logic.
    5. Fall back to backup_analysis() or fallback_response() on failure.
    """
    prompt = f"""
    You are Urban Guardian AI operating in Bengaluru, India.
    Analyze the emergency and return ONLY valid JSON.
    ROUTE ASSIGNMENT RULES — BENGALURU JUNCTIONS:
    Emergencies near or involving Silk Board Junction:
    → route_id = "A"
    Emergencies near or involving BTM Layout / BTM Layout Water Tank Junction:
    → route_id = "B"
    Emergencies near or involving Jayadeva Junction / Jayadeva Hospital area:
    → route_id = "C"
    EMERGENCY TYPE FALLBACK (if no junction is matched):
    1. Cardiac Emergency
    2. Ambulance Emergency
    3. Medical Emergency
    → route_id = "A"  (Silk Board Junction corridor)
    1. Road Accident
    2. Vehicular Accident
    3. Collision
    4. Highway Crash
    → route_id = "B"  (BTM Layout Water Tank Junction corridor)
    1. Fire Emergency
    2. Building Fire
    3. Explosion
    4. Fire Brigade Response
    → route_id = "C"  (Jayadeva Junction corridor)
    IMPORTANT:
    - route_id MUST be exactly A, B, or C.
    - Do not leave route_id empty.
    - Prefer location-based route assignment over type-based.
    - Choose the hospital closest to the emergency location.
    - corridor_required should be true for critical emergencies.
    - In the route array, use real Bengaluru junction names.
    Return ONLY JSON in this format:
    {{
        "severity":"",
        "type":"",
        "location":"",
        "hospital":"",
        "route":[],
        "route_id":"",
        "corridor_required":true,
        "citizen_alert":""
    }}
    Emergency Description:
    {text}
    """
    # --- Attempt Gemini call ---
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            # Strip markdown fences if present
            clean = (
                response.text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )
            # Parse JSON safely
            try:
                data = json.loads(clean)
            except json.JSONDecodeError:
                st.warning("⚠ Gemini returned invalid JSON. Using Backup AI.")
                data = backup_analysis(text) or fallback_response()
        except Exception as e:
            # Covers quota errors, network issues, API failures
            err_msg = str(e).lower()
            if "quota" in err_msg or "rate" in err_msg:
                st.warning("⚠ Gemini API quota exceeded. Using Backup AI.")
            else:
                st.warning("⚠ Gemini unavailable. Using Backup AI.")
            data = backup_analysis(text) or fallback_response()
    else:
        # No API key configured — use backup immediately
        st.warning("⚠ Gemini API key not set. Using Backup AI.")
        data = backup_analysis(text) or fallback_response()
    # --- Safety check: ensure data is a valid dict ---
    if not isinstance(data, dict):
        data = fallback_response()
    # --- Ensure all required keys exist ---
    required_keys = {
        "severity": "Unknown",
        "type": "Emergency",
        "location": "Unknown",
        "hospital": "Nearest Hospital",
        "route": [],
        "route_id": "A",
        "corridor_required": True,
        "citizen_alert": "Emergency in progress. Please clear the route."
    }
    for key, default in required_keys.items():
        if key not in data or data[key] is None or data[key] == "":
            data[key] = default
    # --- Override route_id: location first, emergency type second ---
    # This guarantees the correct Bengaluru junction corridor is activated
    # regardless of what Gemini returned in the route_id field.
    data["route_id"] = resolve_route_id(data["location"], data["type"])
    return data
# =========================================================
# NODEMCU
# =========================================================
def activate_route_a():
    """Activate Silk Board Junction emergency corridor."""
    try:
        r = requests.get(f"http://{NODEMCU_IP}/emergencyA", timeout=2)
        return r.status_code == 200
    except:
        return False
def activate_route_b():
    """Activate BTM Layout Water Tank Junction emergency corridor."""
    try:
        r = requests.get(f"http://{NODEMCU_IP}/emergencyB", timeout=2)
        return r.status_code == 200
    except:
        return False
def activate_route_c():
    """Activate Jayadeva Junction emergency corridor."""
    try:
        r = requests.get(f"http://{NODEMCU_IP}/emergencyC", timeout=2)
        return r.status_code == 200
    except:
        return False
def normal_mode():
    try:
        r = requests.get(f"http://{NODEMCU_IP}/normal", timeout=2)
        return r.status_code == 200
    except:
        return False
def get_status():
    try:
        r = requests.get(f"http://{NODEMCU_IP}/status", timeout=2)
        return r.status_code == 200
    except:
        return False
# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class='hero glow'>
<div class='hero-title'>
🚑 Urban Guardian AI
</div>
<div class='hero-sub'>
Agentic Emergency Response & Smart Traffic Command Center
</div>
</div>
""",
unsafe_allow_html=True)
st.write("")
# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "🚨 Emergency Dashboard",
    "🗺 Smart City View",
    "⚙ Hardware Monitoring"
])
# =========================================================
# TAB 1
# =========================================================
with tab1:
    emergency = st.text_area(
        "🚨 Describe Emergency",
        height=160,
        placeholder="Critical cardiac patient near Silk Board Junction. Heavy traffic congestion..."
    )
    analyze = st.button(
        "Analyze Emergency"
    )
    if analyze:
        with st.spinner(
            "🤖 AI Agents Coordinating..."
        ):
            data = analyze_emergency(emergency)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(
            "Severity",
            data["severity"]
        )
        c2.metric(
            "Location",
            data["location"]
        )
        c3.metric(
            "Hospital",
            data["hospital"]
        )
        c4.metric(
            "Corridor",
            "ACTIVE"
            if data["corridor_required"]
            else "OFF"
        )
        st.divider()
        left, right = st.columns([2, 1])
        with left:
            st.subheader("🧠 AI Analysis")
            st.info(
                f"Emergency Type: {data['type']}"
            )
            st.success(
                f"Recommended Hospital: {data['hospital']}"
            )
            # Show junction name alongside route waypoints
            route_id = data.get("route_id", "A")
            junction_name = ROUTE_JUNCTION.get(route_id, f"Route {route_id}")
            st.write(
                f"**Active Junction:** {junction_name}"
            )
            st.write(
                f"Route: {' ➜ '.join(data['route'])}"
            )
        with right:
            st.subheader("🤖 Agents")
            st.success("Emergency Agent")
            st.success("Hospital Agent")
            st.success("Traffic Agent")
            st.success("Citizen Alert Agent")
        st.divider()
        st.subheader("🚦 Traffic Control")
        if data["corridor_required"]:
            route_id = data.get("route_id", "A")
            junction_name = ROUTE_JUNCTION.get(route_id, f"Route {route_id}")
            if route_id == "A":
                success = activate_route_a()
            elif route_id == "B":
                success = activate_route_b()
            elif route_id == "C":
                success = activate_route_c()
            else:
                success = False
            if success:
                st.success(
                    f"🚦 Emergency Corridor Activated — {junction_name} (Route {route_id})"
                )
            else:
                st.error(
                    "❌ Failed to communicate with NodeMCU"
                )
        else:
            normal_mode()
            st.info("Normal Traffic Mode")
        st.divider()
        st.subheader("📢 Citizen Alert")
        st.warning(data["citizen_alert"])
# =========================================================
# TAB 2
# =========================================================
with tab2:
    st.subheader("🗺 Smart City Route Visualization")
    m = folium.Map(
        location=[12.9279, 77.6271],
        zoom_start=12
    )
    folium.Marker(
        [12.9279, 77.6271],
        popup="🚑 Ambulance"
    ).add_to(m)
    folium.Marker(
        [12.8945, 77.5970],
        popup="🏥 Apollo Hospital"
    ).add_to(m)
    # Route A — Silk Board Junction marker
    folium.Marker(
        [12.9170, 77.6231],
        popup="🟢 Silk Board Junction (Route A)",
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)
    # Route B — BTM Layout Water Tank Junction marker
    folium.Marker(
        [12.9116, 77.6100],
        popup="🔵 BTM Layout Water Tank Junction (Route B)",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    # Route C — Jayadeva Junction marker
    folium.Marker(
        [12.9200, 77.5980],
        popup="🔴 Jayadeva Junction (Route C)",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    folium.PolyLine(
        [
            [12.9279, 77.6271],
            [12.8945, 77.5970]
        ],
        color="lime",
        weight=8
    ).add_to(m)
    st_folium(m, width=1200, height=500)
# =========================================================
# TAB 3
# =========================================================
with tab3:
    st.subheader("⚙ Hardware Monitoring")
    online = get_status()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "NodeMCU",
            "ONLINE" if online else "OFFLINE"
        )
    with col2:
        st.metric("Traffic Corridor", "READY")
    with col3:
        st.metric("Emergency Mode", "STANDBY")
    if online:
        st.success("🟢 NodeMCU Connected Successfully")
        st.divider()
        st.subheader("🚦 Manual Traffic Control — Bengaluru Junctions")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("🚦 Silk Board Junction (A)"):
                if activate_route_a():
                    st.success("🚦 Silk Board Junction Corridor Activated")
                else:
                    st.error("❌ NodeMCU Communication Failed")
        with c2:
            if st.button("🚦 BTM Layout Water Tank Jn. (B)"):
                if activate_route_b():
                    st.success("🚦 BTM Layout Water Tank Junction Corridor Activated")
                else:
                    st.error("❌ NodeMCU Communication Failed")
        with c3:
            if st.button("🚦 Jayadeva Junction (C)"):
                if activate_route_c():
                    st.success("🚦 Jayadeva Junction Corridor Activated")
                else:
                    st.error("❌ NodeMCU Communication Failed")
        with c4:
            if st.button("🔄 Normal"):
                if normal_mode():
                    st.info("🔄 Normal Mode Activated")
                else:
                    st.error("❌ NodeMCU Communication Failed")
    else:
        st.warning("🟡 NodeMCU Not Reachable")
# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption(
    "Powered by Gemini • Agentic AI • ESP8266 • Urban Guardian AI"
)
st.subheader("📊 Impact Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Response Time Saved", "6 min")
c2.metric("Traffic Delay Reduced", "32%")
c3.metric("Emergency Priority", "HIGH")
c4.metric("Corridor Length", "4.2 km")