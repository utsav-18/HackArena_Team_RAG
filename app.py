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