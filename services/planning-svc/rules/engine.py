from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any

from htn.models import Task, WorldState


class RuleViolation(ValueError):
    pass


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    predicate: Callable[[WorldState, Task], bool]
    hard: bool = True
    penalty: float = 0.0
    mission_types: tuple[str, ...] = ()


class RuleEngine:
    """Forward-evaluated tactical rules. Hard failures stop HTN expansion."""

    def __init__(self, rules: list[Rule]):
        self.rules = rules
        self.fired_rule_ids: list[str] = []
        self.soft_penalty = 0.0

    def validate_task(self, state: WorldState, task: Task) -> None:
        mission_type = state.get("mission_type", "")
        for rule in self.rules:
            if rule.mission_types and mission_type not in rule.mission_types:
                continue
            if not rule.predicate(state, task):
                self.fired_rule_ids.append(rule.id)
                if rule.hard:
                    raise RuleViolation(f"{rule.id}: {rule.description}")
                self.soft_penalty += rule.penalty

    def validate_plan(self, state: WorldState, tasks: list[Task]) -> dict:
        self.fired_rule_ids = []
        self.soft_penalty = 0.0
        violations = []
        for task in tasks:
            try:
                self.validate_task(state, task)
            except RuleViolation as error:
                violations.append(str(error))
        return {"valid": not violations, "hard_violations": violations, "soft_penalty": self.soft_penalty, "rule_firings": self.fired_rule_ids}


def _at_least(key: str, amount: float) -> Callable[[WorldState, Task], bool]:
    return lambda state, _task: float(state.get(key, amount)) >= amount


def _at_most(key: str, amount: float) -> Callable[[WorldState, Task], bool]:
    return lambda state, _task: float(state.get(key, 0)) <= amount


def _requires_completion(completed_task: str) -> Callable[[WorldState, Task], bool]:
    return lambda state, task: state.get(f"complete:{completed_task}", False)


def _not_state(key: str, value: Any) -> Callable[[WorldState, Task], bool]:
    return lambda state, _task: state.get(key) != value


def _state_equals(key: str, value: Any) -> Callable[[WorldState, Task], bool]:
    return lambda state, _task: state.get(key) == value


def phase_one_rules() -> list[Rule]:
    ci, ct, log = "COUNTER_INFILTRATION", "COUNTER_TERRORISM", "HIGH_ALTITUDE_LOGISTICS"
    
    all_mission_types = (ci, ct, log)
    return [
        # CI Rules (Counter-Infiltration) - Expanded
        Rule("CI-001", "minimum 3:1 force ratio is required", lambda s, _t: s.get("own_force", 3) >= 3 * s.get("threat_strength", 1), mission_types=(ci,)),
        Rule("CI-002", "forested or mountainous cordon depth must be 500m", lambda s, _t: s.get("terrain") not in {"FORESTED", "MOUNTAINOUS"} or s.get("cordon_depth_m", 500) >= 500, mission_types=(ci,)),
        Rule("CI-003", "graduated force ROE must be enabled", lambda s, _t: bool(s.get("graduated_force", True)), mission_types=(ci,)),
        Rule("CI-004", "night movement without NVD is penalised", lambda s, _t: s.get("time_of_day") != "NIGHT" or bool(s.get("has_nvd", False)), hard=False, penalty=15, mission_types=(ci,)),
        Rule("CI-005", "RF shadow beyond 20km requires a relay", lambda s, _t: not (s.get("rf_shadow") and s.get("hq_distance_km", 0) > 20) or bool(s.get("comms_relay", False)), mission_types=(ci,)),
        Rule("CI-006", "no cross-boundary movement without authority", lambda s, _t: not s.get("cross_boundary", False) or bool(s.get("cross_boundary_authorised", False)), mission_types=(ci,)),
        Rule("CI-007", "sensor correlation precedes threat tracking", lambda s, t: t.name != "TRACK_INFILTRATORS" or bool(s.get("complete:CORRELATE_SENSOR_FEEDS", True)), mission_types=(ci,)),
        Rule("CI-008", "minimum sensor coverage requires 80%", lambda s, _t: s.get("sensor_coverage_percent", 80) >= 80, mission_types=(ci,)),
        Rule("CI-009", "reconnaissance must cover all ingress routes", lambda s, _t: s.get("routes_covered_percent", 85) >= 85, mission_types=(ci,)),
        Rule("CI-010", "communications blackout requires alternative plans", lambda s, _t: not s.get("comms_blackout", False) or bool(s.get("alternate_comms_plan", False)), mission_types=(ci,)),
        Rule("CI-011", "QRT must be positioned within 5km", lambda s, _t: s.get("qrt_distance_km", 5) <= 5, mission_types=(ci,)),
        Rule("CI-012", "observation posts must have clear line of sight", lambda s, _t: s.get("line_of_sight_quality", 0.7) >= 0.7, mission_types=(ci,)),
        Rule("CI-013", "sensor network requires redundancy", lambda s, _t: s.get("sensor_redundancy_factor", 1.5) >= 1.5, mission_types=(ci,)),
        Rule("CI-014", "terrain analysis must be completed before deployment", lambda s, t: t.name != "DEPLOY_BLOCKING_ELEMENTS" or bool(s.get("complete:ASSESS_TERRAIN_CONDITIONS", True)), mission_types=(ci,)),
        Rule("CI-015", "civilian presence requires additional ROE measures", lambda s, _t: not s.get("civilian_presence", False) or bool(s.get("civilian_protection_measures", True)), mission_types=(ci,)),
        Rule("CI-016", "weather conditions affect sensor effectiveness", lambda s, _t: s.get("sensor_weather_effectiveness", 0.6) >= 0.6, hard=False, penalty=12, mission_types=(ci,)),
        Rule("CI-017", "minimum fuel reserve for mobile units required", lambda s, _t: s.get("mobile_fuel_reserve", 0.3) >= 0.3, mission_types=(ci,)),
        Rule("CI-018", "medical evacuation route must be identified", lambda s, _t: bool(s.get("medevac_route_identified", True)), mission_types=(ci,)),
        Rule("CI-019", "command post must be secure", lambda s, _t: bool(s.get("command_post_secure", True)), mission_types=(ci,)),
        Rule("CI-020", "deployment must be staggered to avoid detection", lambda s, _t: s.get("stagger_deployment", True), hard=False, penalty=8, mission_types=(ci,)),
        Rule("CI-021", "minimum 2 hours rest before operation", lambda s, _t: s.get("rest_hours_before", 2) >= 2, mission_types=(ci,)),
        Rule("CI-022", "coordination with local forces required", lambda s, _t: bool(s.get("local_force_coordination", True)), mission_types=(ci,)),
        Rule("CI-023", "QRT must have mechanical support", lambda s, _t: bool(s.get("qrt_mechanical_support", True)), mission_types=(ci,)),
        Rule("CI-024", "sensor calibration must be verified", lambda s, t: t.name != "ACTIVATE_SENSOR_NETWORK" or bool(s.get("complete:VERIFY_SENSOR_CALIBRATION", True)), mission_types=(ci,)),
        Rule("CI-025", "patrol routes must cover full AO", lambda s, _t: s.get("patrol_coverage_percent", 90) >= 90, mission_types=(ci,)),
        
        # CT Rules (Counter-Terrorism) - Expanded
        Rule("CT-001", "hostage survival estimate must be at least 0.85", lambda s, _t: s.get("hostage_survival_probability", 0.85) >= .85, mission_types=(ct,)),
        Rule("CT-002", "civilian casualty probability must not exceed 0.05", lambda s, _t: s.get("civilian_casualty_probability", .05) <= .05, mission_types=(ct,)),
        Rule("CT-003", "hostage position confirmation is required before breach", lambda s, t: t.name != "SIMULTANEOUS_BREACH" or bool(s.get("complete:CONFIRM_HOSTAGE_POSITIONS", True)), mission_types=(ct,)),
        Rule("CT-004", "building isolation precedes assault", lambda s, t: t.name != "SIMULTANEOUS_BREACH" or bool(s.get("complete:CORDON_BUILDING", True)), mission_types=(ct,)),
        Rule("CT-005", "medical support must be allocated for extraction", lambda s, t: t.name != "HOSTAGE_EXTRACTION" or s.get("medical_teams", 1) >= 1, mission_types=(ct,)),
        Rule("CT-006", "lethal force requires ROE authorisation", lambda s, t: t.name != "NEUTRALIZE_THREAT" or bool(s.get("lethal_force_authorised", True)), mission_types=(ct,)),
        Rule("CT-007", "unconfirmed floor plan incurs a soft planning penalty", lambda s, _t: bool(s.get("floor_plan_confirmed", True)), hard=False, penalty=8, mission_types=(ct,)),
        Rule("CT-008", "minimum 3:1 assault force ratio", lambda s, _t: s.get("assault_force_ratio", 3) >= 3, mission_types=(ct,)),
        Rule("CT-009", "breaching team must have ballistic protection", lambda s, _t: bool(s.get("breaching_team_protected", True)), mission_types=(ct,)),
        Rule("CT-010", "communications jammer must be available", lambda s, _t: bool(s.get("comms_jammer_available", True)), mission_types=(ct,)),
        Rule("CT-011", "entry points must be reconnoitered", lambda s, _t: s.get("entry_points_reconned", 2) >= 2, mission_types=(ct,)),
        Rule("CT-012", "negotiation attempt required before assault", lambda s, _t: bool(s.get("negotiation_attempted", True)), hard=False, penalty=10, mission_types=(ct,)),
        Rule("CT-013", "special equipment must be checked", lambda s, t: t.name != "SIMULTANEOUS_BREACH" or bool(s.get("complete:TEST_COMMUNICATION_GEAR", True)), mission_types=(ct,)),
        Rule("CT-014", "hostage profile analysis required", lambda s, _t: bool(s.get("hostage_profile_complete", True)), mission_types=(ct,)),
        Rule("CT-015", "multiple escape routes must be secured", lambda s, _t: s.get("secured_escape_routes", 2) >= 2, mission_types=(ct,)),
        Rule("CT-016", "sniper overwatch available for assault", lambda s, _t: not s.get("requires_sniper", False) or bool(s.get("sniper_available", True)), mission_types=(ct,)),
        Rule("CT-017", "explosive entry requires blast mitigation", lambda s, _t: not s.get("explosive_entry", False) or bool(s.get("blast_mitigation_measures", True)), mission_types=(ct,)),
        Rule("CT-018", "civilians must be cleared from kill zone", lambda s, _t: not s.get("civilians_present", False) or bool(s.get("civilian_cleared", True)), mission_types=(ct,)),
        Rule("CT-019", "medical triage capacity must match potential casualties", lambda s, _t: s.get("medical_capacity_ratio", 1.2) >= 1.2, mission_types=(ct,)),
        Rule("CT-020", "safe room identification required", lambda s, _t: bool(s.get("safe_room_identified", True)), mission_types=(ct,)),
        Rule("CT-021", "decontamination team available if CBRN risk", lambda s, _t: not s.get("cbrn_risk", False) or bool(s.get("cbrn_team_available", True)), mission_types=(ct,)),
        Rule("CT-022", "secondary team for hostage protection", lambda s, _t: s.get("secondary_teams", 1) >= 1, mission_types=(ct,)),
        Rule("CT-023", "rehearsals conducted with all assault teams", lambda s, _t: bool(s.get("rehearsals_complete", True)), mission_types=(ct,)),
        Rule("CT-024", "night vision equipment required for night ops", lambda s, _t: not s.get("night_ops", False) or bool(s.get("has_night_vision", True)), mission_types=(ct,)),
        Rule("CT-025", "post-assault evidence collection plan required", lambda s, _t: bool(s.get("evidence_collection_plan", True)), hard=False, penalty=5, mission_types=(ct,)),
        
        # LOG Rules (High Altitude Logistics) - Expanded
        Rule("LOG-001", "air operations remain below the 7000m ceiling", lambda s, t: t.name != "FLY_SORTIES" or s.get("altitude_m", 0) <= 7000, mission_types=(log,)),
        Rule("LOG-002", "air operations require 500m visibility", lambda s, t: t.name != "FLY_SORTIES" or s.get("visibility_m", 500) >= 500, mission_types=(log,)),
        Rule("LOG-003", "air operations require wind at or below 40 km/h", lambda s, t: t.name != "FLY_SORTIES" or s.get("wind_kmh", 40) <= 40, mission_types=(log,)),
        Rule("LOG-004", "sorties require a serviceable aircraft", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("aircraft_serviceable", True)), mission_types=(log,)),
        Rule("LOG-005", "ground convoy requires route trafficability", lambda s, t: t.name != "GROUND_CONVOY" or bool(s.get("route_trafficable", True)), mission_types=(log,)),
        Rule("LOG-006", "minimum fuel reserve must be preserved", lambda s, _t: s.get("fuel_reserve", .2) >= .2, mission_types=(log,)),
        Rule("LOG-007", "weather uncertainty adds a soft penalty", lambda s, _t: s.get("weather_confidence", .8) >= .6, hard=False, penalty=10, mission_types=(log,)),
        Rule("LOG-008", "payload weight must be within aircraft capacity", lambda s, t: t.name != "FLY_SORTIES" or s.get("payload_weight_kg", 5000) <= s.get("aircraft_capacity_kg", 10000), mission_types=(log,)),
        Rule("LOG-009", "cargo must be properly secured for altitude", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("cargo_secured", True)), mission_types=(log,)),
        Rule("LOG-010", "crew rest requirements must be met", lambda s, _t: s.get("crew_rest_hours", 8) >= 8, mission_types=(log,)),
        Rule("LOG-011", "alternate airfields identified and confirmed", lambda s, _t: s.get("alternate_airfields", 2) >= 2, mission_types=(log,)),
        Rule("LOG-012", "cargo manifest must be completed", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("complete:PREPARE_CARGO_MANIFEST", True)), mission_types=(log,)),
        Rule("LOG-013", "weight and balance calculation required", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("complete:CALCULATE_WEIGHT_AND_BALANCE", True)), mission_types=(log,)),
        Rule("LOG-014", "fuel calculation must account for wind", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("wind_fuel_adjustment_applied", True)), hard=False, penalty=15, mission_types=(log,)),
        Rule("LOG-015", "de-icing equipment available if temperature below 5°C", lambda s, _t: s.get("temperature_c", 15) > 5 or bool(s.get("deicing_available", True)), mission_types=(log,)),
        Rule("LOG-016", "navigation equipment operational", lambda s, _t: bool(s.get("navigation_equipment_operational", True)), mission_types=(log,)),
        Rule("LOG-017", "ground support equipment available", lambda s, _t: bool(s.get("ground_support_available", True)), mission_types=(log,)),
        Rule("LOG-018", "hazardous cargo requires special handling", lambda s, _t: not s.get("hazardous_cargo", False) or bool(s.get("hazardous_handling_procedures", True)), mission_types=(log,)),
        Rule("LOG-019", "air traffic control coordination required", lambda s, _t: bool(s.get("atc_coordination_complete", True)), mission_types=(log,)),
        Rule("LOG-020", "cargo load distribution within limits", lambda s, _t: s.get("load_distribution_factor", 0.85) >= 0.85, mission_types=(log,)),
        Rule("LOG-021", "communication equipment for all aircraft", lambda s, _t: bool(s.get("aircraft_comms_operational", True)), mission_types=(log,)),
        Rule("LOG-022", "rescue equipment must be on board", lambda s, _t: bool(s.get("rescue_equipment_on_board", True)), mission_types=(log,)),
        Rule("LOG-023", "weather forecast obtained for entire route", lambda s, _t: bool(s.get("route_weather_obtained", True)), mission_types=(log,)),
        Rule("LOG-024", "oxygen systems operational for high altitude", lambda s, _t: s.get("altitude_m", 0) <= 4000 or bool(s.get("oxygen_systems_operational", True)), mission_types=(log,)),
        Rule("LOG-025", "flight plan must be filed and approved", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("flight_plan_filed", True)), mission_types=(log,)),
        
        # Cross-Mission General Rules
        Rule("GEN-001", "minimum operational security (OPSEC) required", lambda s, _t: bool(s.get("opsec_measures_enforced", True)), mission_types=all_mission_types),
        Rule("GEN-002", "key personnel must have basic medical training", lambda s, _t: s.get("medical_trained_personnel", 5) >= 5, mission_types=all_mission_types),
        Rule("GEN-003", "communication encryption must be used", lambda s, _t: bool(s.get("communication_encrypted", True)), mission_types=all_mission_types),
        Rule("GEN-004", "emergency action plan must be documented", lambda s, _t: bool(s.get("emergency_action_plan_ready", True)), mission_types=all_mission_types),
        Rule("GEN-005", "operational timings must be synchronized", lambda s, _t: bool(s.get("timings_synchronized", True)), mission_types=all_mission_types),
        Rule("GEN-006", "logistical support chain verified", lambda s, _t: bool(s.get("logistics_chain_verified", True)), mission_types=all_mission_types),
        Rule("GEN-007", "casualty evacuation plan in place", lambda s, _t: bool(s.get("casualty_evacuation_plan", True)), mission_types=all_mission_types),
        Rule("GEN-008", "force protection measures adequate", lambda s, _t: s.get("force_protection_level", 0.7) >= 0.7, mission_types=all_mission_types),
        Rule("GEN-009", "real-time intelligence updates available", lambda s, _t: bool(s.get("intel_updates_available", True)), mission_types=all_mission_types),
        Rule("GEN-010", "secondary communication system operational", lambda s, _t: bool(s.get("secondary_comms_operational", True)), mission_types=all_mission_types),
    ]
