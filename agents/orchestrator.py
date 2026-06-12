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

    # ── Main workflow ─────────────────────────────────────────────────────────

    def run(self, emergency_text: str) -> dict:
        """
        Execute the full multi-agent emergency response workflow.

        Args:
            emergency_text: Raw natural-language emergency description

        Returns a complete response dict:
        {
            "agent_status": {
                "Orchestrator Agent": "✅ Success",
                "Emergency Assessment Agent": "✅ Success",
                "Hospital Coordination Agent": "✅ Success",
                "Traffic Optimization Agent": "✅ Success",
                "Citizen Alert Agent": "✅ Success"
            },
            "execution_logs": [ { agent, status, elapsed_ms, error }, ... ],
            "final_data": {
                "severity": str,
                "type": str,
                "location": str,
                "hospital": str,
                "hospital_contact": str,
                "eta_minutes": int,
                "route": list,
                "route_id": str,
                "junction": str,
                "corridor_required": bool,
                "nodemcu_triggered": bool,
                "nodemcu_status": str,
                "citizen_alert": str,
                "sms_alert": str,
                "broadcast_zones": list,
                "timestamp": str,
                "gemini_used": bool,
            },
            "total_elapsed_ms": int,
            "orchestrator_status": "✅ Success" | "⚠️ Partial" | "❌ Failed"
        }
        """
        workflow_start = time.time()
        execution_logs = []
        agent_status   = {}

        # ── Mark Orchestrator as started ──────────────────────────────────────
        agent_status[self.name] = "✅ Running"

        # ─────────────────────────────────────────────────────────────────────
        # STEP 1 — Emergency Assessment Agent (Gemini called here — ONCE)
        # ─────────────────────────────────────────────────────────────────────
        assessment, log1 = self._run_agent(
            self._emergency_agent, emergency_text
        )
        execution_logs.append(log1)
        agent_status[self._emergency_agent.name] = log1["status"]

        if assessment is None:
            # Hard fallback if agent itself crashes
            assessment = {
                "severity": "Critical",
                "type": "Cardiac Emergency",
                "location": "Silk Board Junction",
                "gemini_used": False,
                "status": "fallback",
            }

        # ─────────────────────────────────────────────────────────────────────
        # STEP 2 — Hospital Coordination Agent (rule-based)
        # ─────────────────────────────────────────────────────────────────────
        hospital_data, log2 = self._run_agent(
            self._hospital_agent, assessment
        )
        execution_logs.append(log2)
        agent_status[self._hospital_agent.name] = log2["status"]

        if hospital_data is None:
            hospital_data = {
                "hospital": "Apollo Hospital",
                "hospital_contact": "+91-80-2941-4444",
                "eta_minutes": 8,
                "selection_reason": "fallback",
                "status": "fallback",
            }

        # ─────────────────────────────────────────────────────────────────────
        # STEP 3 — Traffic Optimization Agent (decision + NodeMCU IoT)
        # ─────────────────────────────────────────────────────────────────────
        traffic_data, log3 = self._run_agent(
            self._traffic_agent, assessment, hospital_data
        )
        execution_logs.append(log3)
        agent_status[self._traffic_agent.name] = log3["status"]

        if traffic_data is None:
            traffic_data = {
                "route_id": "A",
                "route": ["Silk Board Junction", "Apollo Hospital"],
                "junction": "Silk Board Junction",
                "corridor_required": True,
                "nodemcu_triggered": False,
                "nodemcu_status": "Agent error — fallback data used",
                "status": "fallback",
            }

        # ─────────────────────────────────────────────────────────────────────
        # STEP 4 — Citizen Alert Agent (template-based)
        # ─────────────────────────────────────────────────────────────────────
        citizen_data, log4 = self._run_agent(
            self._citizen_agent, assessment, hospital_data, traffic_data
        )
        execution_logs.append(log4)
        agent_status[self._citizen_agent.name] = log4["status"]

        if citizen_data is None:
            citizen_data = {
                "citizen_alert": "Emergency in progress. Please clear the route.",
                "sms_alert": "URBAN GUARDIAN: Emergency active.",
                "broadcast_zones": ["Bengaluru"],
                "timestamp": "",
                "status": "fallback",
            }

        # ── Mark Orchestrator complete ────────────────────────────────────────
        agent_status[self.name] = "✅ Success"

        # ─────────────────────────────────────────────────────────────────────
        # Aggregate Final Data
        # ─────────────────────────────────────────────────────────────────────
        final_data = {
            # From Emergency Assessment Agent
            "severity"         : assessment.get("severity", "Unknown"),
            "type"             : assessment.get("type", "Emergency"),
            "location"         : assessment.get("location", "Unknown"),
            "gemini_used"      : assessment.get("gemini_used", False),
            # From Hospital Coordination Agent
            "hospital"         : hospital_data.get("hospital", "Nearest Hospital"),
            "hospital_contact" : hospital_data.get("hospital_contact", "N/A"),
            "eta_minutes"      : hospital_data.get("eta_minutes", 0),
            # From Traffic Optimization Agent
            "route_id"         : traffic_data.get("route_id", "A"),
            "route"            : traffic_data.get("route", []),
            "junction"         : traffic_data.get("junction", ""),
            "corridor_required": traffic_data.get("corridor_required", True),
            "nodemcu_triggered": traffic_data.get("nodemcu_triggered", False),
            "nodemcu_status"   : traffic_data.get("nodemcu_status", ""),
            # From Citizen Alert Agent
            "citizen_alert"    : citizen_data.get("citizen_alert", ""),
            "sms_alert"        : citizen_data.get("sms_alert", ""),
            "broadcast_zones"  : citizen_data.get("broadcast_zones", []),
            "timestamp"        : citizen_data.get("timestamp", ""),
        }

        # Determine overall status
        failed = [l for l in execution_logs if "❌" in l["status"]]
        if not failed:
            orchestrator_status = "✅ Success"
        elif len(failed) < len(execution_logs):
            orchestrator_status = "⚠️ Partial"
        else:
            orchestrator_status = "❌ Failed"

        total_elapsed = round((time.time() - workflow_start) * 1000)

        return {
            "agent_status"       : agent_status,
            "execution_logs"     : execution_logs,
            "final_data"         : final_data,
            "total_elapsed_ms"   : total_elapsed,
            "orchestrator_status": orchestrator_status,
        }


# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json
    orch = OrchestratorAgent()
    result = orch.run(
        "Critical cardiac patient near Silk Board Junction. "
        "Heavy traffic. Ambulance needed immediately."
    )
    print(json.dumps(result, indent=2, default=str))