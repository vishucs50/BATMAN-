from __future__ import annotations

import httpx
import uuid
import structlog
from dataclasses import dataclass

from cbr.engine import Case, CaseBasedReasoner
from htn.models import WorldState
from htn.planner import HTNPlanner
from rules.engine import RuleEngine

from constraint.aco import ConstraintOptimizer, Assignment

logger = structlog.get_logger(__name__)


@dataclass
class COA:
    id: str
    name: str
    style: str
    task_hierarchy: dict
    estimated_duration_min: int
    required_resources: dict[str, float]
    assumptions: list[str]
    utility_score: float
    cbr_matches: list[str]
    validation: dict


class COAGenerator:
    """Generates doctrine-valid bold, balanced, and cautious alternatives."""

    styles = {
        "BOLD": {"duration": .85, "risk": .78, "assumption": "Higher tempo is acceptable within approved ROE."},
        "BALANCED": {"duration": 1.0, "risk": .90, "assumption": "Doctrine baseline resource posture is available."},
        "CAUTIOUS": {"duration": 1.20, "risk": .97, "assumption": "Additional time is available for force protection measures."},
    }

    def __init__(self, planner: HTNPlanner, rule_engine: RuleEngine, cbr: CaseBasedReasoner):
        self.planner, self.rule_engine, self.cbr = planner, rule_engine, cbr

    def generate(self, mission_type: str, facts: dict) -> list[COA]:
        state = WorldState({**facts, "mission_type": mission_type})
        query = Case("query", mission_type, facts.get("terrain", "UNKNOWN"), facts.get("primary_threat", "UNKNOWN"), facts.get("resource_readiness", .8), facts.get("urgency", .5), "SUCCESS")
        matches = self.cbr.retrieve(query, 3)
        result: list[COA] = []
        
        # ── Fetch Threat Assessments from threat-svc ──
        if mission_type == "COUNTER_INFILTRATION":
            threat_types = ["INFILTRATION"]
        elif mission_type == "COUNTER_TERRORISM":
            threat_types = ["AMBUSH", "IED"]
        elif mission_type == "HIGH_ALTITUDE_LOGISTICS":
            threat_types = ["IED"]
        else:
            threat_types = ["INFILTRATION"]
            
        visibility = facts.get("visibility_m", 5000)
        weather_str = facts.get("initial_weather", "CLEAR")
        if weather_str in ("FOG", "RAIN", "SNOW") and "visibility_m" not in facts:
            visibility = 800 if weather_str == "FOG" else 2000
            
        time_of_day = facts.get("time_of_day", "NIGHT")
        
        payload = {
            "mission_id": facts.get("mission_id", str(uuid.uuid4())),
            "threat_types": threat_types,
            "sensor_alerts": facts.get("sensor_alerts", []),
            "historical_pattern_match": float(facts.get("historical_pattern_match", 0.5)),
            "weather_conditions": {
                "visibility_m": float(visibility),
                "wind_speed_kmh": float(facts.get("wind_speed_kmh", 12.0)),
                "precipitation": float(facts.get("precipitation", 0.0))
            },
            "time_of_day": time_of_day
        }
        
        threat_assessments = []
        try:
            with httpx.Client(timeout=5.0) as client:
                threat_resp = client.post("http://127.0.0.1:8004/threats/assess", json=payload)
                threat_resp.raise_for_status()
                threat_assessments = threat_resp.json()
                logger.info("fetched_threat_assessments", count=len(threat_assessments))
        except Exception as e:
            logger.warning("failed_to_fetch_threats", error=str(e))
            
        max_threat_risk = max([t.get("risk_score", 0.0) for t in threat_assessments]) / 10.0 if threat_assessments else float(facts.get("threat_probability", 0.2))
        
        # Instantiate ACO constraint solver with reduced ants/iterations to prevent gateway timeouts
        optimizer = ConstraintOptimizer(ants=8, iterations=12, seed=42)
        base_units = facts.get("units", [f"unit-{i:03d}" for i in range(1, 46)])
        # Generate virtual unit instances (e.g. unit-001_0, unit-001_1) to support multiple tasks per physical unit
        units = [f"{unit}_{slot}" for unit in base_units for slot in range(2)]
        
        for style, modifier in self.styles.items():
            plan = self.planner.plan(mission_type, state)
            resources: dict[str, float] = {}
            for task in plan.executable_tasks:
                for resource, amount in task.required_resources.items():
                    resources[resource] = resources.get(resource, 0) + amount
            duration = max(1, round(plan.estimated_duration_min * modifier["duration"]))
            validation = self.rule_engine.validate_plan(state, plan.executable_tasks)
            
            # ACO Optimization
            # Dynamically scale budgets to ensure feasibility given task count
            num_tasks = len(plan.executable_tasks)
            fuel_budget = float(facts.get("fuel_budget", max(1000.0, num_tasks * 50.0)))
            resource_budget = float(facts.get("resource_budget", max(2000.0, num_tasks * 100.0)))

            assignments = []
            for task in plan.executable_tasks:
                for unit in units:
                    task_fuel = task.required_resources.get("fuel", 0.0)
                    fuel_cost = (task_fuel * 100.0) if task_fuel > 0 else 5.0
                    
                    task_res = sum(task.required_resources.values())
                    res_cost = (task_res * 10.0) if task_res > 0 else 2.0
                    
                    unit_id_base = unit.split("_")[0]
                    unit_idx = int(unit_id_base.split("-")[-1]) if "-" in unit_id_base and unit_id_base.split("-")[-1].isdigit() else 1
                    fuel_cost *= (1.0 + (unit_idx % 3 - 1) * 0.1)
                    res_cost *= (1.0 + (unit_idx % 4 - 2) * 0.05)
                    
                    spec = unit_idx % 4
                    suitability = 0.5
                    if spec == 0 and any(k in task.required_resources for k in ["comms", "signals", "intelligence"]):
                        suitability = 0.95
                    elif spec == 1 and any(k in task.required_resources for k in ["personnel", "combat"]):
                        suitability = 0.90
                    elif spec == 2 and any(k in task.required_resources for k in ["medical", "logistics"]):
                        suitability = 0.85
                    elif spec == 3 and any(k in task.required_resources for k in ["aviation", "vehicles", "drones"]):
                        suitability = 0.90
                        
                    hard_eligible = True
                    if "aviation" in task.required_resources and spec != 3:
                        hard_eligible = False
                    if "medical" in task.required_resources and spec != 2:
                        hard_eligible = False
                        
                    assignments.append(Assignment(
                        unit_id=unit,
                        task_id=task.name,
                        fuel_cost=round(fuel_cost, 2),
                        resource_cost=round(res_cost, 2),
                        suitability=round(suitability, 2),
                        hard_eligible=hard_eligible
                    ))
            
            logger.info("aco_optimization_started", plan_style=style, task_count=len(plan.executable_tasks), units_count=len(units))
            aco_result = optimizer.optimize(assignments, fuel_budget, resource_budget)
            logger.info("aco_optimization_completed", plan_style=style, score=aco_result.score, assignments_count=len(aco_result.assignments))
            
            validation["aco_score"] = round(aco_result.score, 4)
            validation["aco_fuel_used"] = round(aco_result.fuel_used, 4)
            validation["aco_resource_used"] = round(aco_result.resource_used, 4)
            validation["aco_assignments"] = [{"unit_id": a.unit_id.split("_")[0], "task_id": a.task_id} for a in aco_result.assignments]
            
            if len(aco_result.assignments) < len(plan.executable_tasks):
                validation["valid"] = False
                validation.setdefault("hard_violations", []).append("ACO Constraint: Infeasible resource allocation within budget limits.")
            
            # Store threat info in validation
            validation["threat_assessments"] = threat_assessments
            validation["max_threat_risk"] = max_threat_risk
            
            # Penalize utility according to style sensitivity to threat risk
            if style == "BOLD":
                style_risk_penalty = 0.3 * max_threat_risk
            elif style == "BALANCED":
                style_risk_penalty = 0.15 * max_threat_risk
            else:  # CAUTIOUS
                style_risk_penalty = 0.05 * max_threat_risk
                
            risk_term = max(0.0, modifier["risk"] - style_risk_penalty)
            
            aco_factor = (aco_result.score / len(plan.executable_tasks)) if plan.executable_tasks else 0.0
            utility = round((.35 * risk_term) + (.15 * (1 / modifier["duration"])) + (.10 * aco_factor) + (.04 if validation["valid"] else 0) - validation["soft_penalty"] / 100, 4)
            
            result.append(COA(str(uuid.uuid4()), f"{mission_type.replace('_', ' ').title()} — {style.title()}", style, plan.hierarchy.as_dict(), duration, resources, [modifier["assumption"], "Commander approval is required before execution."], utility, [case.id for case, _score in matches], validation))
        # ── Call Wargame Service for real Monte Carlo simulation and scoring ──
        wargame_url = "http://127.0.0.1:8003/wargame/evaluate"
        coas_payload = []
        for coa in result:
            coas_payload.append({
                "coa_id": coa.id,
                "task_hierarchy": coa.task_hierarchy,
                "estimated_duration_min": coa.estimated_duration_min,
                "required_resources": coa.required_resources,
                "assumptions": list(coa.assumptions)
            })
            
        payload = {
            "mission_id": facts.get("mission_id", str(uuid.uuid4())),
            "mission_type": mission_type,
            "coas": coas_payload,
            "world_state": {
                "terrain": facts.get("terrain", "PLAINS"),
                "elevation_m": float(facts.get("elevation_m", 0.0)),
                "slope_degrees": float(facts.get("slope_degrees", 0.0)),
                "trafficability": float(facts.get("trafficability", 1.0)),
                "vegetation_density": float(facts.get("vegetation_density", 0.0)),
                "initial_weather": facts.get("initial_weather", "CLEAR"),
                "threat_probability": max_threat_risk,
                "civilian_density": float(facts.get("civilian_density", 0.1)),
                "comms_baseline": float(facts.get("comms_baseline", 0.95)),
                "fuel_available": float(facts.get("fuel_available", 1.0)),
                "ammunition_available": float(facts.get("ammunition_available", 1.0))
            },
            "threat_probability": max_threat_risk,
            "mc_runs": int(facts.get("mc_runs", 50)),
            "parallel_workers": 4
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                wargame_resp = client.post(wargame_url, json=payload)
                wargame_resp.raise_for_status()
                evaluated_scores = wargame_resp.json()
                logger.info("fetched_wargame_scores", count=len(evaluated_scores))
                
                score_map = {s["coa_id"]: s for s in evaluated_scores}
                for coa in result:
                    if coa.id in score_map:
                        score_data = score_map[coa.id]
                        # Preserve planner utility score
                        coa.validation["planner_utility"] = coa.utility_score
                        # Update final utility score to the simulation derived score
                        coa.utility_score = score_data["utility_score"]
                        coa.validation["simulation_score"] = score_data
        except Exception as e:
            logger.warning("failed_to_fetch_wargame_scores", error=str(e))
            
        return sorted(result, key=lambda coa: coa.utility_score, reverse=True)

