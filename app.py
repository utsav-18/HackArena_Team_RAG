# app.py
# Urban Guardian AI — HackArena Edition
# Multi-Agent Agentic AI + Generative AI Emergency Response System
# ──────────────────────────────────────────────────────────────────
# Architecture:
#   Orchestrator → Emergency Assessment Agent (Gemini ×1)
#              → Hospital Coordination Agent  (rule-based)
#              → Traffic Optimization Agent   (decision + IoT)
#              → Citizen Alert Agent          (template)
# ──────────────────────────────────────────────────────────────────

import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Urban Guardian AI",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Import Agents ─────────────────────────────────────────────────────────────
from agents.orchestrator import OrchestratorAgent
from agents.traffic_agent import (
    activate_route_a, activate_route_b, activate_route_c,
    normal_mode, get_status,
)

# ── Constants ─────────────────────────────────────────────────────────────────
ROUTE_JUNCTION = {
    "A": "Silk Board Junction",
    "B": "BTM Layout Water Tank Junction",
    "C": "Jayadeva Junction",
}

ROUTE_COLORS = {"A": "green", "B": "blue", "C": "red"}

JUNCTION_COORDS = {
    "A": [12.9170, 77.6231],
    "B": [12.9116, 77.6100],
    "C": [12.9200, 77.5980],
}

HOSPITAL_COORDS = {
    "Apollo Hospital":                          [12.8945, 77.5970],
    "Narayana Health City":                     [12.8600, 77.5800],
    "Jayadeva Institute of Cardiovascular Sciences": [12.9204, 77.5973],
    "Victoria Hospital":                        [12.9716, 77.5716],
    "Manipal Hospital":                         [12.9592, 77.6470],
}


# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS — Futuristic Dark Theme with Agent Status Styling
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #020617 0%, #0f172a 40%, #0a0f1e 70%, #020617 100%);
    min-height: 100vh;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── HERO ── */
.hero {
    text-align: center;
    padding: 36px 20px 28px;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(0,255,255,0.07) 0%, rgba(37,99,235,0.10) 100%);
    border: 1px solid rgba(0,255,255,0.20);
    box-shadow: 0 0 60px rgba(0,255,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 8px;
}
.hero-title {
    font-size: 54px;
    font-weight: 800;
    background: linear-gradient(90deg, #00ffff, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}
.hero-badge {
    display: inline-block;
    background: rgba(0,255,255,0.10);
    border: 1px solid rgba(0,255,255,0.30);
    color: #00ffff;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.hero-sub {
    color: #94a3b8;
    font-size: 17px;
    margin-top: 6px;
}

/* ── METRICS ── */
[data-testid="metric-container"] {
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(0,255,255,0.12);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 0 20px rgba(0,255,255,0.05);
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 0 35px rgba(0,255,255,0.20);
    border-color: rgba(0,255,255,0.35);
}

/* ── BUTTONS ── */
.stButton > button {
    width: 100%;
    height: 52px;
    border: none;
    border-radius: 14px;
    color: white;
    font-size: 16px;
    font-weight: 700;
    background: linear-gradient(90deg, #06b6d4, #2563eb);
    box-shadow: 0 0 25px rgba(37,99,235,0.30);
    transition: all 0.25s ease;
    letter-spacing: 0.3px;
}
.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 40px rgba(0,255,255,0.45);
}

/* ── TEXT AREA ── */
textarea {
    background: rgba(15,23,42,0.85) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(0,255,255,0.18) !important;
    border-radius: 16px !important;
    font-size: 15px !important;
    transition: border-color 0.3s;
}
textarea:focus { border-color: rgba(0,255,255,0.50) !important; }

/* ── GLASS CARD ── */
.glass {
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 22px;
    padding: 22px;
}

/* ── AGENT STATUS PANEL ── */
.agent-panel {
    background: rgba(15,23,42,0.90);
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 22px;
    padding: 20px;
    margin-bottom: 6px;
}
.agent-panel-title {
    color: #00ffff;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.agent-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-radius: 12px;
    margin-bottom: 8px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    transition: background 0.2s;
}
.agent-row:hover { background: rgba(0,255,255,0.04); }
.agent-name {
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 600;
}
.agent-badge-success {
    background: rgba(34,197,94,0.15);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.30);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
}
.agent-badge-pending {
    background: rgba(234,179,8,0.15);
    color: #fbbf24;
    border: 1px solid rgba(234,179,8,0.30);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
}
.agent-badge-fail {
    background: rgba(239,68,68,0.15);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.30);
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
}
.agent-ms {
    color: #475569;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    margin-left: 8px;
}
.gemini-badge {
    background: linear-gradient(90deg, rgba(0,255,255,0.15), rgba(99,102,241,0.15));
    border: 1px solid rgba(0,255,255,0.30);
    color: #a5f3fc;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;
    letter-spacing: 1px;
}
.ai-rule-badge {
    background: rgba(100,116,139,0.15);
    border: 1px solid rgba(100,116,139,0.20);
    color: #64748b;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 10px;
}

/* ── SEVERITY CHIPS ── */
.chip-critical { color: #f87171; font-weight: 700; }
.chip-high     { color: #fb923c; font-weight: 700; }
.chip-medium   { color: #fbbf24; font-weight: 700; }
.chip-low      { color: #4ade80; font-weight: 700; }

/* ── WORKFLOW DIAGRAM ── */
.workflow-step {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: rgba(255,255,255,0.025);
    border-left: 3px solid rgba(0,255,255,0.30);
    border-radius: 0 10px 10px 0;
    margin-bottom: 4px;
    font-size: 13px;
    color: #94a3b8;
}
.workflow-arrow {
    text-align: center;
    color: rgba(0,255,255,0.40);
    font-size: 16px;
    line-height: 1;
    margin: 2px 0;
}

/* ── PULSE ANIMATION ── */
@keyframes pulse-glow {
    0%   { box-shadow: 0 0 15px rgba(0,255,255,0.08); }
    50%  { box-shadow: 0 0 40px rgba(0,255,255,0.28); }
    100% { box-shadow: 0 0 15px rgba(0,255,255,0.08); }
}
.glow { animation: pulse-glow 3s ease-in-out infinite; }

@keyframes slide-in {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.slide-in { animation: slide-in 0.4s ease forwards; }

/* ── ALERT BOXES ── */
.alert-box {
    background: rgba(15,23,42,0.85);
    border-radius: 16px;
    padding: 18px 22px;
    border-left: 4px solid #00ffff;
    margin: 8px 0;
    color: #e2e8f0;
    font-size: 14px;
    line-height: 1.6;
}
.sms-box {
    background: rgba(15,23,42,0.70);
    border-radius: 12px;
    padding: 12px 16px;
    border: 1px dashed rgba(99,102,241,0.40);
    color: #a5b4fc;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
}

/* ── NODEMCU STATUS ── */
.iot-success {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #4ade80;
    font-size: 13px;
}
.iot-warning {
    background: rgba(234,179,8,0.08);
    border: 1px solid rgba(234,179,8,0.25);
    border-radius: 12px;
    padding: 12px 16px;
    color: #fbbf24;
    font-size: 13px;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.80);
    border-radius: 16px;
    padding: 4px;
    border: 1px solid rgba(0,255,255,0.10);
}
[data-baseweb="tab"] {
    border-radius: 12px !important;
    color: #64748b !important;
    font-weight: 600;
}
[aria-selected="true"] {
    background: rgba(0,255,255,0.12) !important;
    color: #00ffff !important;
}

/* ── DIVIDER ── */
hr { border-color: rgba(0,255,255,0.08) !important; }

/* ── STREAMLIT INFO / SUCCESS / ERROR ── */
[data-testid="stAlert"] {
    border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)
