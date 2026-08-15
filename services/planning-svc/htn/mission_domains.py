"""Doctrine-shaped HTN domains for the three Phase 1 mission profiles."""
from __future__ import annotations

from .domain import Domain, Method, Operator
from .models import Task, WorldState


def _primitive(name: str, duration: int, **resources: float) -> Task:
    return Task(name, primitive=True, duration_min=duration, required_resources=resources)


def _operator(task_name: str) -> Operator:
    return Operator(task_name, effect=lambda _state, task: {f"complete:{task.name}": True})


def build_phase_one_domain() -> Domain:
    domain = Domain()
    definitions = {
        "COUNTER_INFILTRATION": [
            ("Detect_and_Localise", [("Deploy_Surveillance_Grid", [_primitive("POSITION_QRT", 12, personnel=12), _primitive("ACTIVATE_SENSOR_NETWORK", 5, sensors=1), _primitive("ESTABLISH_OBSERVATION_POSTS", 15, personnel=6)]), ("Process_Sensor_Data", [_primitive("CORRELATE_SENSOR_FEEDS", 8, comms=1), _primitive("TRACK_INFILTRATORS", 10, personnel=2)])]),
            ("Contain_and_Block", [("Seal_Escape_Routes", [_primitive("IDENTIFY_CHOKEPOINTS", 10, gis=1), _primitive("DEPLOY_BLOCKING_ELEMENTS", 20, personnel=18)]), ("Establish_Cordon", [_primitive("ASSIGN_GRID_SQUARES", 8, personnel=9)])]),
            ("ROE_Compliant_Resolution", [("Resolve_Threat", [_primitive("CLOSE_WITH_THREAT", 15, personnel=12), _primitive("APPLY_GRADUATED_FORCE", 5, personnel=6)])]),
        ],
        "COUNTER_TERRORISM": [
            ("Intelligence_and_Planning", [("Prepare_Assault", [_primitive("GATHER_FLOOR_PLAN", 10, intelligence=1), _primitive("CONFIRM_HOSTAGE_POSITIONS", 12, intelligence=1), _primitive("REHEARSE_BREACH", 20, personnel=12)])]),
            ("Isolation", [("Isolate_Site", [_primitive("CORDON_BUILDING", 15, personnel=18), _primitive("EVACUATE_CIVILIANS", 15, personnel=6), _primitive("CUT_COMMS", 5, signals=1)])]),
            ("Assault_and_Extraction", [("Execute_Assault", [_primitive("SIMULTANEOUS_BREACH", 8, personnel=16), _primitive("HOSTAGE_EXTRACTION", 12, medical=1), _primitive("NEUTRALIZE_THREAT", 10, personnel=10)])]),
        ],
        "HIGH_ALTITUDE_LOGISTICS": [
            ("Demand_and_Window_Assessment", [("Assess_Demand", [_primitive("ASSESS_DEMAND", 10, logistics=1), _primitive("FORECAST_WEATHER_WINDOW", 8, weather=1), _primitive("CHECK_AIRCRAFT_SERVICEABILITY", 10, aviation=1)])]),
            ("Load_Planning", [("Plan_Load", [_primitive("COMPUTE_PAYLOAD_ALTITUDE_DEGRADATION", 8, logistics=1), _primitive("OPTIMIZE_LOAD_DISTRIBUTION", 12, logistics=1)])]),
            ("Execution_and_Confirmation", [("Deliver_Supplies", [_primitive("FLY_SORTIES", 45, aviation=1, fuel=0.25), _primitive("GROUND_CONVOY", 60, vehicles=2, fuel=0.2), _primitive("CONFIRM_RECEIPT", 5, comms=1)])]),
        ],
    }
    for mission_type, operations in definitions.items():
        root = f"MISSION:{mission_type}"
        domain.add_method(Method(root, f"{mission_type.lower()}_workflow", lambda _s, _t, ops=operations: [Task(name) for name, _tasks in ops]))
        for operation, tasks in operations:
            domain.add_method(Method(operation, f"{operation.lower()}_method", lambda _s, _t, items=tasks: [Task(name) for name, _subs in items]))
            for task, subtasks in tasks:
                domain.add_method(Method(task, f"{task.lower()}_method", lambda _s, _t, children=subtasks: children))
                for subtask in subtasks:
                    domain.add_operator(_operator(subtask.name))
    return domain
