from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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


def phase_one_rules() -> list[Rule]:
    ci, ct, log = "COUNTER_INFILTRATION", "COUNTER_TERRORISM", "HIGH_ALTITUDE_LOGISTICS"
    return [
        Rule("CI-001", "minimum 3:1 force ratio is required", lambda s, _t: s.get("own_force", 3) >= 3 * s.get("threat_strength", 1), mission_types=(ci,)),
        Rule("CI-002", "forested or mountainous cordon depth must be 500m", lambda s, _t: s.get("terrain") not in {"FORESTED", "MOUNTAINOUS"} or s.get("cordon_depth_m", 500) >= 500, mission_types=(ci,)),
        Rule("CI-003", "graduated force ROE must be enabled", lambda s, _t: bool(s.get("graduated_force", True)), mission_types=(ci,)),
        Rule("CI-004", "night movement without NVD is penalised", lambda s, _t: s.get("time_of_day") != "NIGHT" or bool(s.get("has_nvd", False)), hard=False, penalty=15, mission_types=(ci,)),
        Rule("CI-005", "RF shadow beyond 20km requires a relay", lambda s, _t: not (s.get("rf_shadow") and s.get("hq_distance_km", 0) > 20) or bool(s.get("comms_relay", False)), mission_types=(ci,)),
        Rule("CI-006", "no cross-boundary movement without authority", lambda s, _t: not s.get("cross_boundary", False) or bool(s.get("cross_boundary_authorised", False)), mission_types=(ci,)),
        Rule("CI-007", "sensor correlation precedes threat tracking", lambda s, t: t.name != "TRACK_INFILTRATORS" or bool(s.get("complete:CORRELATE_SENSOR_FEEDS", True)), mission_types=(ci,)),
        Rule("CT-001", "hostage survival estimate must be at least 0.85", lambda s, _t: s.get("hostage_survival_probability", 0.85) >= .85, mission_types=(ct,)),
        Rule("CT-002", "civilian casualty probability must not exceed 0.05", lambda s, _t: s.get("civilian_casualty_probability", .05) <= .05, mission_types=(ct,)),
        Rule("CT-003", "hostage position confirmation is required before breach", lambda s, t: t.name != "SIMULTANEOUS_BREACH" or bool(s.get("complete:CONFIRM_HOSTAGE_POSITIONS", True)), mission_types=(ct,)),
        Rule("CT-004", "building isolation precedes assault", lambda s, t: t.name != "SIMULTANEOUS_BREACH" or bool(s.get("complete:CORDON_BUILDING", True)), mission_types=(ct,)),
        Rule("CT-005", "medical support must be allocated for extraction", lambda s, t: t.name != "HOSTAGE_EXTRACTION" or s.get("medical_teams", 1) >= 1, mission_types=(ct,)),
        Rule("CT-006", "lethal force requires ROE authorisation", lambda s, t: t.name != "NEUTRALIZE_THREAT" or bool(s.get("lethal_force_authorised", True)), mission_types=(ct,)),
        Rule("CT-007", "unconfirmed floor plan incurs a soft planning penalty", lambda s, _t: bool(s.get("floor_plan_confirmed", True)), hard=False, penalty=8, mission_types=(ct,)),
        Rule("LOG-001", "air operations remain below the 7000m ceiling", lambda s, t: t.name != "FLY_SORTIES" or s.get("altitude_m", 0) <= 7000, mission_types=(log,)),
        Rule("LOG-002", "air operations require 500m visibility", lambda s, t: t.name != "FLY_SORTIES" or s.get("visibility_m", 500) >= 500, mission_types=(log,)),
        Rule("LOG-003", "air operations require wind at or below 40 km/h", lambda s, t: t.name != "FLY_SORTIES" or s.get("wind_kmh", 40) <= 40, mission_types=(log,)),
        Rule("LOG-004", "sorties require a serviceable aircraft", lambda s, t: t.name != "FLY_SORTIES" or bool(s.get("aircraft_serviceable", True)), mission_types=(log,)),
        Rule("LOG-005", "ground convoy requires route trafficability", lambda s, t: t.name != "GROUND_CONVOY" or bool(s.get("route_trafficable", True)), mission_types=(log,)),
        Rule("LOG-006", "minimum fuel reserve must be preserved", lambda s, _t: s.get("fuel_reserve", .2) >= .2, mission_types=(log,)),
        Rule("LOG-007", "weather uncertainty adds a soft penalty", lambda s, _t: s.get("weather_confidence", .8) >= .6, hard=False, penalty=10, mission_types=(log,)),
    ]
