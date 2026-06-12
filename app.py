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
