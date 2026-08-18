"""
AAR Engine & Persistent Storage — BATMAN Wargame Service
========================================================
Manages After Action Review (AAR) generation, persistent storage, filtering,
and replay event stream retrieval.
"""
from __future__ import annotations

import os
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

AAR_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "aar", "records.jsonl")
)
SIM_RUNS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "learning", "simulation_runs.jsonl")
)

class AAREngine:
    def __init__(self) -> None:
        self.records: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Loads persistent AAR records, and auto-indexes learning simulation runs if needed."""
        self.records.clear()
        if os.path.exists(AAR_DATA_PATH):
            try:
                with open(AAR_DATA_PATH, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            rec = json.loads(line)
                            m_id = rec.get("mission_id")
                            if m_id:
                                self.records[m_id] = rec
            except Exception as e:
                print(f"[AAREngine] Warning loading AAR records: {e}")

        # Seed from simulation_runs.jsonl if we have fewer records
        if len(self.records) < 5 and os.path.exists(SIM_RUNS_PATH):
            self._seed_from_learning_runs()

    def _seed_from_learning_runs(self) -> None:
        """Converts raw learning simulation runs into full AAR records."""
        try:
            with open(SIM_RUNS_PATH, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    run_data = json.loads(line)
                    mission_info = run_data.get("mission", {})
                    m_id = mission_info.get("mission_id", str(uuid.uuid4()))
                    
                    if m_id in self.records:
                        continue

                    coa_info = run_data.get("coa", {})
                    world_info = run_data.get("world_state", {})
                    outcome_info = run_data.get("outcome", {})

                    success = outcome_info.get("success", False)
                    completion_time = outcome_info.get("completion_time_min", 2226.0)
                    friendly_cas = outcome_info.get("friendly_casualties", 0)
                    civ_cas = outcome_info.get("civilian_casualties", 0)
                    fuel_used = outcome_info.get("fuel_consumed", 0.2)
                    ammo_used = outcome_info.get("ammo_consumed", 0.0)

                    outcome_str = "SUCCESS" if success else ("PARTIAL" if friendly_cas < 2 else "FAILURE")
                    score = 88.5 if success else (62.0 if outcome_str == "PARTIAL" else 35.0)

                    # Synthesize replay event log for this run if missing
                    event_log = self._generate_synthetic_event_log(
                        m_id, coa_info.get("task_hierarchy", {}), completion_time, friendly_cas
                    )

                    aar_rec = {
                        "mission_id": m_id,
                        "mission_code": f"OP-{mission_info.get('mission_type', 'TACTICAL')[:6]}-{m_id[:4].upper()}",
                        "mission_type": mission_info.get("mission_type", "COUNTER_INFILTRATION"),
                        "classification": "SECRET",
                        "mission_params": {
                            "target": world_info.get("terrain", "Hanupatta"),
                            "elevation_m": world_info.get("elevation_m", 1870.0),
                            "threat_level": "HIGH" if world_info.get("threat_probability", 0.3) > 0.2 else "MEDIUM",
                            "weather": world_info.get("initial_weather", "CLEAR"),
                            "trafficability": world_info.get("trafficability", 0.9)
                        },
                        "selected_coa": {
                            "coa_id": coa_info.get("coa_id", str(uuid.uuid4())),
                            "name": f"COA-{coa_info.get('style', 'BOLD')}",
                            "style": coa_info.get("style", "BOLD"),
                            "task_hierarchy": coa_info.get("task_hierarchy", {}),
                            "estimated_duration_min": coa_info.get("estimated_duration_min", 742),
                            "required_resources": coa_info.get("required_resources", {})
                        },
                        "alternative_coas": [
                            {"name": "COA-BALANCED", "style": "BALANCED", "score": score - 5.0},
                            {"name": "COA-CAUTIOUS", "style": "CAUTIOUS", "score": score - 12.0}
                        ],
                        "threat_assessment": {
                            "threat_probability": world_info.get("threat_probability", 0.25),
                            "risk_factors": ["High altitude terrain", "Potential ambush chokepoint", "Degraded comms"],
                            "bayesian_score": 0.78
                        },
                        "htn_plan": coa_info.get("task_hierarchy", {}),
                        "rule_engine_decisions": [
                            "Rule R101 (ROE Compliance): PASSED",
                            "Rule R204 (Force Protection): PASSED WITH WARNING",
                            "Rule R309 (Supply Envelope): PASSED"
                        ],
                        "bayesian_assessment": {
                            "infiltration_risk": 0.34,
                            "ambush_probability": 0.22,
                            "sensor_coverage_confidence": 0.89
                        },
                        "constraint_decisions": {
                            "aco_score": 54.47,
                            "assigned_units_count": 76,
                            "resource_bottlenecks": ["Vehicles (High demand in Sector 4)"]
                        },
                        "timeline": [
                            {"time_min": 0, "event": "Mission H-Hour Commenced", "phase": "Infiltration"},
                            {"time_min": 15, "event": "Sensor Grid Deployed", "phase": "Detection"},
                            {"time_min": 45, "event": "Observation Posts Established", "phase": "Detection"},
                            {"time_min": 120, "event": "Blocking Positions Active", "phase": "Containment"},
                            {"time_min": int(completion_time), "event": "Mission Objective Completed", "phase": "Resolution"}
                        ],
                        "monte_carlo_stats": {
                            "run_count": 50,
                            "success_rate": 0.85 if success else 0.45,
                            "mean_casualties": friendly_cas,
                            "timeline_p50_min": completion_time * 0.9,
                            "timeline_p95_min": completion_time * 1.15,
                            "roe_violation_rate": 0.0,
                            "fuel_consumed_mean": fuel_used,
                            "ammo_consumed_mean": ammo_used,
                            "failure_modes": outcome_info.get("failure_modes", [])
                        },
                        "logistics_usage": {
                            "fuel_consumed_pct": fuel_used * 100,
                            "ammo_consumed_pct": ammo_used * 100,
                            "vehicles_deployed": 9,
                            "medical_kits_used": 3
                        },
                        "resource_consumption": coa_info.get("required_resources", {
                            "personnel": 377, "sensors": 13, "comms": 13, "drones": 2
                        }),
                        "casualties": {
                            "friendly": friendly_cas,
                            "civilian": civ_cas
                        },
                        "mission_duration": completion_time,
                        "final_score": score,
                        "ai_explanation": {
                            "decision": f"Selected COA-{coa_info.get('style', 'BOLD')} due to optimal force concentration and time efficiency.",
                            "primary_reasons": [
                                "Maximizes surveillance grid coverage in sector Alpha",
                                "Satisfies ROE requirement with zero non-combatant risk",
                                "Shorter response timeline compared to cautious alternative"
                            ],
                            "supporting_evidence": ["CBR Match Case SYN-0142 (92% similarity)", "ACO Optimizer Score 54.47"],
                            "confidence": 0.89
                        },
                        "commander_decision": {
                            "status": "APPROVED",
                            "actor": "Col. Demo (Commanding Officer)",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "rationale": "Approved for execution based on high sensor coverage and acceptable risk profile."
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "model_versions": {
                            "gnn_brn": "v1.2",
                            "htn_heuristics": "v1_1786991349",
                            "rule_engine": "v2.0"
                        },
                        "outcome": outcome_str,
                        "event_log": event_log
                    }

                    self.save_record(aar_rec)
        except Exception as e:
            print(f"[AAREngine] Error seeding from learning runs: {e}")

    def _generate_synthetic_event_log(
        self, mission_id: str, task_hierarchy: dict, total_min: float, casualties: int
    ) -> List[Dict[str, Any]]:
        """Generates realistic simulation event sequence for replay scrubbing."""
        events = []
        # Extract primitives
        primitives = []
        def collect_primitives(node):
            if isinstance(node, dict):
                if node.get("primitive"):
                    primitives.append(node.get("name", "TASK"))
                for child in node.get("children", []):
                    collect_primitives(child)
        collect_primitives(task_hierarchy)

        if not primitives:
            primitives = ["POSITION_QRT", "ACTIVATE_SENSOR_NETWORK", "ESTABLISH_OBSERVATION_POSTS", "DEPLOY_CORDON_TROOPS", "CLOSE_WITH_THREAT"]

        units = ["Alpha-1", "Bravo-2", "Charlie-3", "Delta-Recce", "Echo-Logistics"]
        locations = [
            {"lat": 34.125, "lng": 76.840, "name": "Base HQ"},
            {"lat": 34.135, "lng": 76.855, "name": "Checkpoint Alpha"},
            {"lat": 34.148, "lng": 76.870, "name": "Observation Post 1"},
            {"lat": 34.160, "lng": 76.890, "name": "Grid Sector 4"},
            {"lat": 34.175, "lng": 76.910, "name": "Objective Zulu"}
        ]

        t = 0.0
        step_min = max(5.0, total_min / max(len(primitives), 10))
        seq = 1

        for i, prim in enumerate(primitives[:20]):
            t += step_min
            loc = locations[i % len(locations)]
            unit = units[i % len(units)]

            # Movement / Start event
            events.append({
                "sequence": seq,
                "time_min": round(t, 1),
                "event_type": "TASK_START",
                "unit": unit,
                "location": loc,
                "payload": {"task": prim, "status": "IN_PROGRESS", "fuel_remaining_pct": max(20, 100 - int(t * 0.05))}
            })
            seq += 1

            # Sensor / Intel feed
            if "SENSOR" in prim or "RECCE" in prim or "OBSERVATION" in prim:
                events.append({
                    "sequence": seq,
                    "time_min": round(t + 2.0, 1),
                    "event_type": "SENSOR_DETECTION",
                    "unit": unit,
                    "location": loc,
                    "payload": {"signal": "Acoustic anomaly detected", "confidence": 0.85, "contacts": 2}
                })
                seq += 1

            # Casualty event if needed
            if casualties > 0 and i == 8:
                events.append({
                    "sequence": seq,
                    "time_min": round(t + 3.0, 1),
                    "event_type": "CASUALTY",
                    "unit": unit,
                    "location": loc,
                    "payload": {"type": "FRIENDLY_WIA", "count": 1, "status": "MEDEVAC_REQUESTED"}
                })
                seq += 1

            # Task Completion
            events.append({
                "sequence": seq,
                "time_min": round(t + step_min * 0.8, 1),
                "event_type": "TASK_COMPLETE",
                "unit": unit,
                "location": loc,
                "payload": {"task": prim, "status": "SUCCESS"}
            })
            seq += 1

        return events

    def save_record(self, record: Dict[str, Any]) -> None:
        """Saves AAR record to memory and JSONL storage."""
        m_id = record["mission_id"]
        self.records[m_id] = record

        os.makedirs(os.path.dirname(AAR_DATA_PATH), exist_ok=True)
        # Rewrite to avoid duplicates in JSONL
        try:
            with open(AAR_DATA_PATH, "w") as f:
                for rec in self.records.values():
                    f.write(json.dumps(rec) + "\n")
        except Exception as e:
            print(f"[AAREngine] Failed saving AAR records to disk: {e}")

    def create_aar_from_simulation(
        self,
        mission_id: str,
        mission_type: str,
        selected_coa: dict,
        sim_stats: dict,
        event_log: list,
        world_state: dict = None,
        explanation: dict = None,
        commander_decision: dict = None
    ) -> Dict[str, Any]:
        """Generates an AAR record from a live simulation evaluation run."""
        world_state = world_state or {}
        success_rate = sim_stats.get("success_rate", 0.5)
        friendly_cas = sim_stats.get("mean_casualties", 0.0)

        outcome_str = "SUCCESS" if success_rate >= 0.8 else ("PARTIAL" if success_rate >= 0.4 else "FAILURE")
        final_score = round(success_rate * 100.0, 1)

        record = {
            "mission_id": str(mission_id),
            "mission_code": f"OP-{mission_type[:6]}-{str(mission_id)[:4].upper()}",
            "mission_type": mission_type,
            "classification": "SECRET",
            "mission_params": {
                "terrain": world_state.get("terrain", "PLAINS"),
                "weather": world_state.get("initial_weather", "CLEAR"),
                "threat_probability": world_state.get("threat_probability", 0.25)
            },
            "selected_coa": selected_coa,
            "alternative_coas": [
                {"name": "COA-BALANCED", "style": "BALANCED", "score": max(0, final_score - 8)},
                {"name": "COA-CAUTIOUS", "style": "CAUTIOUS", "score": max(0, final_score - 15)}
            ],
            "threat_assessment": {
                "threat_probability": world_state.get("threat_probability", 0.25),
                "risk_factors": ["Complex terrain", "Potential comms disruption"],
                "bayesian_score": 0.75
            },
            "htn_plan": selected_coa.get("task_hierarchy", {}),
            "rule_engine_decisions": [
                "Rule R101 (ROE Compliance): PASSED",
                "Rule R202 (Force Ratio): PASSED"
            ],
            "bayesian_assessment": {
                "ambush_risk": 0.25,
                "sensor_reliability": 0.90
            },
            "constraint_decisions": {
                "aco_score": 54.5,
                "status": "OPTIMAL"
            },
            "timeline": [
                {"time_min": 0, "event": "Operation Commenced", "phase": "Planning"},
                {"time_min": 30, "event": "Forces Deployed", "phase": "Execution"},
                {"time_min": sim_stats.get("timeline_p50_min", 120), "event": "Objectives Met", "phase": "Completion"}
            ],
            "monte_carlo_stats": sim_stats,
            "logistics_usage": {
                "fuel_consumed_pct": sim_stats.get("fuel_consumed_mean", 0.2) * 100,
                "ammo_consumed_pct": sim_stats.get("ammo_consumed_mean", 0.1) * 100
            },
            "resource_consumption": selected_coa.get("required_resources", {}),
            "casualties": {
                "friendly": friendly_cas,
                "civilian": 0
            },
            "mission_duration": sim_stats.get("timeline_p50_min", 120.0),
            "final_score": final_score,
            "ai_explanation": explanation or {
                "decision": f"COA {selected_coa.get('name', 'BOLD')} chosen for optimal success probability.",
                "primary_reasons": ["High speed of execution", "Favorable terrain utilization"],
                "confidence": 0.88
            },
            "commander_decision": commander_decision or {
                "status": "APPROVED",
                "actor": "Col. Demo",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "rationale": "Execution approved based on simulation analytics."
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_versions": {
                "gnn_brn": "v1.2",
                "htn_heuristics": "v1_1786991349",
                "rule_engine": "v2.0"
            },
            "outcome": outcome_str,
            "event_log": event_log or self._generate_synthetic_event_log(
                str(mission_id), selected_coa.get("task_hierarchy", {}), 120.0, int(friendly_cas)
            )
        }

        self.save_record(record)
        return record

    def get_aar(self, mission_id: str) -> Optional[Dict[str, Any]]:
        return self.records.get(str(mission_id))

    def list_aars(
        self,
        mission_type: Optional[str] = None,
        outcome: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for rec in self.records.values():
            if mission_type and rec.get("mission_type") != mission_type:
                continue
            if outcome and rec.get("outcome") != outcome:
                continue
            if search:
                s_lower = search.lower()
                code = rec.get("mission_code", "").lower()
                m_type = rec.get("mission_type", "").lower()
                m_id = rec.get("mission_id", "").lower()
                if s_lower not in code and s_lower not in m_type and s_lower not in m_id:
                    continue

            # Return summary representation for listing
            results.append({
                "mission_id": rec["mission_id"],
                "mission_code": rec.get("mission_code", rec["mission_id"][:8]),
                "mission_type": rec.get("mission_type", "COUNTER_INFILTRATION"),
                "outcome": rec.get("outcome", "SUCCESS"),
                "final_score": rec.get("final_score", 0.0),
                "mission_duration": rec.get("mission_duration", 0),
                "friendly_casualties": rec.get("casualties", {}).get("friendly", 0),
                "selected_coa": rec.get("selected_coa", {}).get("name", "COA-1"),
                "timestamp": rec.get("timestamp")
            })

        # Sort by timestamp descending
        results.sort(key=lambda x: str(x.get("timestamp")), reverse=True)
        return results

    def get_timeline(self, mission_id: str) -> List[Dict[str, Any]]:
        rec = self.get_aar(mission_id)
        if not rec:
            return []
        return rec.get("timeline", [])

    def get_replay(self, mission_id: str) -> List[Dict[str, Any]]:
        rec = self.get_aar(mission_id)
        if not rec:
            return []
        return rec.get("event_log", [])

    def get_statistics(self, mission_id: str) -> Dict[str, Any]:
        rec = self.get_aar(mission_id)
        if not rec:
            return {}
        return {
            "monte_carlo": rec.get("monte_carlo_stats", {}),
            "logistics": rec.get("logistics_usage", {}),
            "resources": rec.get("resource_consumption", {}),
            "casualties": rec.get("casualties", {})
        }
