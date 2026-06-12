# agents/orchestrator.py
# Urban Guardian AI — Orchestrator Agent
# ──────────────────────────────────────────────────────────────────────────────
# ROLE   : Master coordinator. Runs all agents in sequence, passes JSON between
#          them, tracks status, measures timing, and returns the final payload.
# FLOW   : EmergencyAssessmentAgent → HospitalCoordinationAgent →
#          TrafficOptimizationAgent → CitizenAlertAgent
# GEMINI : Called exactly ONCE inside EmergencyAssessmentAgent only.
# ──────────────────────────────────────────────────────────────────────────────

import time
import traceback
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.emergency_agent import EmergencyAssessmentAgent
from agents.hospital_agent  import HospitalCoordinationAgent
from agents.traffic_agent   import TrafficOptimizationAgent
from agents.citizen_agent   import CitizenAlertAgent


# ─── Orchestrator ─────────────────────────────────────────────────────────────

class OrchestratorAgent:
    """
    Agent E — Orchestrator Agent
    Coordinates the four specialist agents.
    Does NOT call Gemini itself — only EmergencyAssessmentAgent does.
    """

    name = "Orchestrator Agent"

    def __init__(self):
        self._emergency_agent = EmergencyAssessmentAgent()
        self._hospital_agent  = HospitalCoordinationAgent()
        self._traffic_agent   = TrafficOptimizationAgent()
        self._citizen_agent   = CitizenAlertAgent()

    # ── Internal runner with timing & error capture ───────────────────────────

    def _run_agent(self, agent, *args) -> tuple[dict | None, dict]:
        """
        Execute a single agent safely.
        Returns (result_dict, log_entry).
        """
        start = time.time()
        log = {
            "agent": agent.name,
            "status": "pending",
            "elapsed_ms": 0,
            "error": None,
        }
        try:
            result = agent.run(*args)
            log["status"] = "✅ Success"
            log["elapsed_ms"] = round((time.time() - start) * 1000)
            return result, log
        except Exception as e:
            log["status"] = "❌ Failed"
            log["elapsed_ms"] = round((time.time() - start) * 1000)
            log["error"] = str(e)
            traceback.print_exc()
            return None, log