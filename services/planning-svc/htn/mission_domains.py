"""Doctrine-shaped HTN domains for the three Phase 1 mission profiles."""
from __future__ import annotations

from .domain import Domain, Method, Operator
from .models import Task, WorldState


import os
import json

_HEURISTICS_CACHE = None

def get_heuristic_duration(name: str, default: int) -> int:
    global _HEURISTICS_CACHE
    if _HEURISTICS_CACHE is not None:
        return _HEURISTICS_CACHE.get(name, default)
    try:
        registry_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai/models/registry.yaml"))
        if os.path.exists(registry_path):
            import yaml
            with open(registry_path, "r") as f:
                reg = yaml.safe_load(f)
                active_heuristics = reg.get("active_heuristics")
                if active_heuristics:
                    heur_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai/models/heuristics", active_heuristics))
                    if os.path.exists(heur_path):
                        with open(heur_path, "r") as hf:
                            _HEURISTICS_CACHE = json.load(hf)
                            return _HEURISTICS_CACHE.get(name, default)
    except Exception:
        pass
    _HEURISTICS_CACHE = {}
    return default

def _primitive(name: str, duration: int, **resources: float) -> Task:
    adjusted_duration = get_heuristic_duration(name, duration)
    return Task(name, primitive=True, duration_min=adjusted_duration, required_resources=resources)


def _operator(task_name: str) -> Operator:
    return Operator(task_name, effect=lambda _state, task: {f"complete:{task.name}": True})


def build_phase_one_domain() -> Domain:
    domain = Domain()
    definitions = {
        "COUNTER_INFILTRATION": [
            ("Detect_and_Localise", [
                ("Deploy_Surveillance_Grid", [
                    _primitive("POSITION_QRT", 12, personnel=12),
                    _primitive("ACTIVATE_SENSOR_NETWORK", 5, sensors=1),
                    _primitive("ESTABLISH_OBSERVATION_POSTS", 15, personnel=6),
                    _primitive("DEPLOY_SEISMIC_SENSORS", 8, sensors=2, personnel=4),
                    _primitive("SETUP_ACOUSTIC_MONITORING", 6, sensors=1, personnel=3),
                    _primitive("DEPLOY_THERMAL_IMAGING", 10, sensors=2, personnel=5),
                    _primitive("ESTABLISH_COMMS_RELAY", 7, comms=1, personnel=2),
                    _primitive("POSITION_MOBILE_SENSORS", 9, sensors=3, personnel=6),
                    _primitive("DEPLOY_GROUND_RADAR", 14, sensors=2, personnel=8),
                    _primitive("SETUP_DRONE_SURVEILLANCE", 11, drones=2, personnel=4),
                ]),
                ("Process_Sensor_Data", [
                    _primitive("CORRELATE_SENSOR_FEEDS", 8, comms=1),
                    _primitive("TRACK_INFILTRATORS", 10, personnel=2),
                    _primitive("ANALYSE_PATTERN_DATA", 12, intelligence=2),
                    _primitive("IDENTIFY_INFILTRATION_ROUTES", 9, intelligence=1),
                    _primitive("ESTIMATE_THREAT_TIMELINE", 7, intelligence=1),
                    _primitive("FUSION_DATA_INTEGRATION", 15, comms=2),
                    _primitive("VERIFY_SENSOR_CALIBRATION", 6, personnel=3),
                    _primitive("ESTABLISH_TRACK_HISTORY", 11, intelligence=2),
                ]),
                ("Intelligence_Analysis", [
                    _primitive("REVIEW_INTEL_REPORTS", 14, intelligence=2),
                    _primitive("CROSS_REFERENCE_SOURCES", 10, intelligence=2, comms=1),
                    _primitive("UPDATE_THREAT_ASSESSMENT", 8, intelligence=1),
                    _primitive("IDENTIFY_VULNERABILITIES", 12, intelligence=2),
                    _primitive("ASSESS_OPFOR_CAPABILITIES", 16, intelligence=3),
                ]),
            ]),
            ("Contain_and_Block", [
                ("Seal_Escape_Routes", [
                    _primitive("IDENTIFY_CHOKEPOINTS", 10, gis=1),
                    _primitive("DEPLOY_BLOCKING_ELEMENTS", 20, personnel=18),
                    _primitive("ESTABLISH_ROADBLOCKS", 12, personnel=10, vehicles=2),
                    _primitive("SECURE_PERIMETER_POINTS", 16, personnel=14),
                    _primitive("DEPLOY_BARRIER_MATERIALS", 18, vehicles=3, personnel=12),
                    _primitive("SETUP_CHECKPOINTS", 10, personnel=8, vehicles=1),
                    _primitive("ESTABLISH_KILL_ZONES", 14, personnel=10),
                ]),
                ("Establish_Cordon", [
                    _primitive("ASSIGN_GRID_SQUARES", 8, personnel=9),
                    _primitive("DEPLOY_CORDON_TROOPS", 15, personnel=20),
                    _primitive("SETUP_OBSERVATION_POINTS", 12, personnel=8),
                    _primitive("ESTABLISH_COMMS_NETWORK", 10, comms=2, personnel=4),
                    _primitive("IMPLEMENT_ACCESS_CONTROL", 9, personnel=6),
                    _primitive("CONDUCT_PATROL_ROUTES", 20, personnel=12, vehicles=2),
                ]),
                ("Area_Denial", [
                    _primitive("DEPLOY_OBSTACLES", 16, personnel=15),
                    _primitive("ESTABLISH_MINE_WARNING", 12, personnel=6),
                    _primitive("CREATE_AMBUSH_POSITIONS", 18, personnel=12),
                    _primitive("DEPLOY_TRIP_WIRES", 8, personnel=4),
                    _primitive("SETUP_SURPRISE_ELEMENTS", 14, personnel=10),
                ]),
            ]),
            ("ROE_Compliant_Resolution", [
                ("Resolve_Threat", [
                    _primitive("CLOSE_WITH_THREAT", 15, personnel=12),
                    _primitive("APPLY_GRADUATED_FORCE", 5, personnel=6),
                    _primitive("CALL_FOR_BACKUP", 8, comms=1),
                    _primitive("ESCALATE_THREAT_RESPONSE", 10, personnel=8),
                    _primitive("COORDINATE_TEAM_MOVEMENT", 12, personnel=6, comms=1),
                    _primitive("EXECUTE_APPREHENSION", 18, personnel=10),
                    _primitive("PROCESS_DETAINEES", 14, personnel=8),
                ]),
                ("Negotiation_Response", [
                    _primitive("ESTABLISH_COMMUNICATION", 9, comms=2),
                    _primitive("PRESENT_DEMANDS", 7, personnel=3),
                    _primitive("NEGOTIATE_SURRENDER", 20, personnel=5, comms=1),
                    _primitive("MEDIATE_CONFLICT", 16, personnel=4),
                    _primitive("PREPARE_CONTINGENCY", 12, personnel=6),
                ]),
                ("Force_Protection", [
                    _primitive("DEPLOY_COVER_ELEMENTS", 10, personnel=8),
                    _primitive("ESTABLISH_SECURE_PERIMETER", 14, personnel=12),
                    _primitive("IMPLEMENT_EVASION_TACTICS", 8, personnel=6),
                    _primitive("CONDUCT_FORCE_PROTECTION", 11, personnel=8),
                    _primitive("MAINTAIN_SITUATIONAL_AWARENESS", 6, personnel=4),
                ]),
            ]),
            ("Reconnaissance_Support", [
                ("Gather_Intelligence", [
                    _primitive("DEPLOY_RECCE_TEAMS", 15, personnel=8),
                    _primitive("COLLECT_ENVIRONMENTAL_DATA", 10, sensors=2),
                    _primitive("DOCUMENT_OPFOR_POSITIONS", 12, personnel=4),
                    _primitive("ASSESS_TERRAIN_CONDITIONS", 8, personnel=2),
                    _primitive("MAP_INFRASTRUCTURE", 14, gis=2, personnel=3),
                ]),
                ("Intelligence_Dissemination", [
                    _primitive("COMPILE_INTELLIGENCE_REPORT", 10, intelligence=2),
                    _primitive("DISTRIBUTE_INTELLIGENCE", 6, comms=1),
                    _primitive("BRIEF_COMMAND_ELEMENTS", 8, personnel=3),
                    _primitive("UPDATE_OPERATIONAL_PICTURE", 9, intelligence=1),
                ]),
            ]),
            ("Logistics_Support", [
                ("Supply_Management", [
                    _primitive("ESTABLISH_SUPPLY_ROUTES", 18, logistics=2),
                    _primitive("MAINTAIN_EQUIPMENT", 14, personnel=6),
                    _primitive("MANAGE_AMMUNITION", 10, logistics=1),
                    _primitive("COORDINATE_FUEL_SYSTEMS", 12, logistics=1),
                    _primitive("IMPLEMENT_WASTE_MANAGEMENT", 8, personnel=4),
                ]),
                ("Medical_Support", [
                    _primitive("ESTABLISH_AID_STATIONS", 12, medical=2),
                    _primitive("PREPARE_EVACUATION", 10, medical=1, vehicles=1),
                    _primitive("TRAIN_MEDICAL_PERSONNEL", 16, personnel=8),
                    _primitive("COORDINATE_CASUALTY_CARE", 9, medical=2),
                ]),
            ]),
        ],
        "COUNTER_TERRORISM": [
            ("Intelligence_and_Planning", [
                ("Prepare_Assault", [
                    _primitive("GATHER_FLOOR_PLAN", 10, intelligence=1),
                    _primitive("CONFIRM_HOSTAGE_POSITIONS", 12, intelligence=1),
                    _primitive("REHEARSE_BREACH", 20, personnel=12),
                    _primitive("ANALYSE_BUILDING_STRUCTURE", 14, intelligence=2),
                    _primitive("IDENTIFY_ENTRY_POINTS", 8, intelligence=1),
                    _primitive("PLAN_ROOM_CLEARING", 16, personnel=8),
                    _primitive("COORDINATE_TEAM_ASSIGNMENTS", 10, personnel=6),
                    _primitive("INTEGRATE_SNIPER_SUPPORT", 12, personnel=4),
                ]),
                ("Threat_Assessment", [
                    _primitive("ASSESS_OPFOR_STRENGTH", 15, intelligence=2),
                    _primitive("EVALUATE_BOOBY_TRAP_RISK", 12, intelligence=1),
                    _primitive("ANALYSE_HOSTAGE_SITUATION", 13, intelligence=2),
                    _primitive("DETERMINE_TIMING_CONSIDERATIONS", 10, intelligence=1),
                    _primitive("IDENTIFY_ESCAPE_ROUTES", 9, intelligence=1),
                ]),
                ("Operational_Planning", [
                    _primitive("DEVELOP_CONTINGENCY_PLANS", 18, personnel=6),
                    _primitive("ESTABLISH_OBJECTIVES", 8, personnel=4),
                    _primitive("ALLOCATE_SPECIAL_EQUIPMENT", 12, logistics=2),
                    _primitive("COORDINATE_WITH_AGENCIES", 14, comms=2),
                    _primitive("FINALIZE_ASSIGNMENTS", 10, personnel=6),
                ]),
            ]),
            ("Isolation", [
                ("Isolate_Site", [
                    _primitive("CORDON_BUILDING", 15, personnel=18),
                    _primitive("EVACUATE_CIVILIANS", 15, personnel=6),
                    _primitive("CUT_COMMS", 5, signals=1),
                    _primitive("ESTABLISH_EXCLUSION_ZONE", 12, personnel=10),
                    _primitive("DEPLOY_BARRICADES", 14, personnel=12),
                    _primitive("SETUP_SECURITY_PERIMETER", 11, personnel=8),
                    _primitive("COORDINATE_POLICE_SUPPORT", 10, comms=1),
                ]),
                ("Communication_Control", [
                    _primitive("JAM_HOSTILE_COMMS", 8, signals=2),
                    _primitive("MONITOR_COMMUNICATIONS", 14, comms=2, personnel=4),
                    _primitive("ESTABLISH_SECURE_CHANNELS", 10, comms=2),
                    _primitive("INTERCEPT_ENEMY_TRANSMISSIONS", 12, signals=1),
                ]),
                ("Situation_Containment", [
                    _primitive("CONTAIN_THREAT_RADIUS", 16, personnel=14),
                    _primitive("IMPLEMENT_TRAFFIC_CONTROL", 10, personnel=6),
                    _primitive("COORDINATE_EMERGENCY_SERVICES", 12, comms=2),
                    _primitive("MANAGE_PUBLIC_INFORMATION", 8, personnel=4),
                ]),
            ]),
            ("Assault_and_Extraction", [
                ("Execute_Assault", [
                    _primitive("SIMULTANEOUS_BREACH", 8, personnel=16),
                    _primitive("HOSTAGE_EXTRACTION", 12, medical=1),
                    _primitive("NEUTRALIZE_THREAT", 10, personnel=10),
                    _primitive("CLEAR_ROOMS_SEQUENTIALLY", 18, personnel=12),
                    _primitive("COORDINATE_FLASHBANG_USE", 6, personnel=4),
                    _primitive("PROVIDE_COVER_FIRE", 14, personnel=8),
                    _primitive("SECURE_EXTRACTION_ROUTE", 10, personnel=6),
                ]),
                ("Post_Assault_Operations", [
                    _primitive("SECURE_CRIME_SCENE", 20, personnel=8),
                    _primitive("PROCESS_HOSTAGES", 15, medical=2, personnel=4),
                    _primitive("COLLECT_EVIDENCE", 12, personnel=4),
                    _primitive("DEBRIEF_TEAM_MEMBERS", 10, personnel=6),
                    _primitive("PROCESS_DETAINEES", 16, personnel=8),
                ]),
                ("Casualty_Management", [
                    _primitive("TRIAGE_CASUALTIES", 14, medical=3),
                    _primitive("EVACUATE_WOUNDED", 10, medical=2, vehicles=2),
                    _primitive("ESTABLISH_MEDICAL_TRIAGE", 12, medical=2),
                    _primitive("COORDINATE_HOSPITAL_TRANSFER", 8, comms=1),
                ]),
            ]),
            ("Crisis_Negotiation", [
                ("Negotiation_Phase", [
                    _primitive("OPEN_COMMUNICATION_CHANNELS", 7, comms=2),
                    _primitive("ASSESS_DEMANDS", 12, intelligence=2),
                    _primitive("DEVELOP_NEGOTIATION_STRATEGY", 15, personnel=4),
                    _primitive("CONDUCT_NEGOTIATIONS", 25, personnel=4, comms=1),
                ]),
                ("Psychological_Operations", [
                    _primitive("CONDUCT_PSYOPS", 14, personnel=6),
                    _primitive("MANAGE_INFORMATION_FLOW", 10, comms=2),
                    _primitive("INFLUENCE_HOSTAGE_SITUATION", 12, intelligence=1),
                ]),
            ]),
            ("Technical_Support", [
                ("Electronic_Operations", [
                    _primitive("DEPLOY_ELECTRONIC_MONITORING", 12, signals=2),
                    _primitive("CONDUCT_SURVEILLANCE", 16, sensors=2),
                    _primitive("ANALYSE_TARGET_COMMUNICATIONS", 14, signals=1),
                    _primitive("DEPLOY_TECHNICAL_MEASURES", 10, signals=2),
                ]),
                ("Equipment_Support", [
                    _primitive("PREPARE_BREACHING_GEAR", 8, logistics=1),
                    _primitive("TEST_COMMUNICATION_GEAR", 6, comms=1),
                    _primitive("CALIBRATE_WEAPON_SYSTEMS", 10, personnel=4),
                    _primitive("PREPARE_SPECIAL_EQUIPMENT", 12, logistics=2),
                ]),
            ]),
        ],
        "HIGH_ALTITUDE_LOGISTICS": [
            ("Demand_and_Window_Assessment", [
                ("Assess_Demand", [
                    _primitive("ASSESS_DEMAND", 10, logistics=1),
                    _primitive("FORECAST_WEATHER_WINDOW", 8, weather=1),
                    _primitive("CHECK_AIRCRAFT_SERVICEABILITY", 10, aviation=1),
                    _primitive("ANALYSE_SUPPLY_PRIORITIES", 12, logistics=2),
                    _primitive("DETERMINE_CRITICAL_SUPPLIES", 14, logistics=2),
                    _primitive("EVALUATE_ALTITUDE_IMPACT", 9, weather=1),
                    _primitive("ASSESS_ROUTE_WEATHER_RISK", 11, weather=2),
                    _primitive("CALCULATE_WEIGHT_AND_BALANCE", 8, aviation=1),
                ]),
                ("Resource_Planning", [
                    _primitive("ESTIMATE_FUEL_REQUIREMENTS", 12, logistics=2),
                    _primitive("PLAN_CREW_REST_PERIODS", 10, personnel=4),
                    _primitive("COORDINATE_AIRCRAFT_SCHEDULE", 14, aviation=2),
                    _primitive("ALLOCATE_CARGO_SPACE", 9, logistics=1),
                    _primitive("DETERMINE_PRIORITY_CARGO", 11, logistics=2),
                ]),
                ("Environmental_Assessment", [
                    _primitive("MONITOR_WEATHER_TRENDS", 15, weather=2),
                    _primitive("EVALUATE_TERRAIN_OBSTACLES", 12, gis=2),
                    _primitive("ASSESS_ATMOSPHERIC_CONDITIONS", 10, weather=1),
                    _primitive("IDENTIFY_ALTERNATE_ROUTES", 13, gis=2),
                    _primitive("CHECK_AERODROME_CONDITIONS", 8, aviation=1),
                ]),
            ]),
            ("Load_Planning", [
                ("Plan_Load", [
                    _primitive("COMPUTE_PAYLOAD_ALTITUDE_DEGRADATION", 8, logistics=1),
                    _primitive("OPTIMIZE_LOAD_DISTRIBUTION", 12, logistics=1),
                    _primitive("DETERMINE_PACKAGING_REQUIREMENTS", 10, logistics=2),
                    _primitive("ASSESS_WEIGHT_LIMITS", 9, aviation=1),
                    _primitive("PLAN_CARGO_SECUREMENT", 14, personnel=4),
                    _primitive("CALCULATE_CENTER_OF_GRAVITY", 11, logistics=2),
                    _primitive("PREPARE_CARGO_MANIFEST", 7, logistics=1),
                ]),
                ("Loading_Operations", [
                    _primitive("SUPERVISE_LOADING", 15, personnel=6),
                    _primitive("SECURE_CARGO", 12, personnel=8),
                    _primitive("VERIFY_WEIGHT_DISTRIBUTION", 10, personnel=4),
                    _primitive("INSPECT_CARGO_CONDITION", 8, personnel=3),
                    _primitive("DOCUMENT_LOAD_CONFIGURATION", 9, logistics=1),
                ]),
                ("Special_Cargo_Handling", [
                    _primitive("HANDLE_HAZARDOUS_MATERIALS", 18, personnel=8),
                    _primitive("PREPARE_PERISHABLE_CARGO", 14, logistics=2),
                    _primitive("ORGANIZE_OUTSIZED_CARGO", 16, personnel=6),
                    _primitive("IMPLEMENT_COLD_CHAIN", 12, logistics=1),
                ]),
            ]),
            ("Execution_and_Confirmation", [
                ("Deliver_Supplies", [
                    _primitive("FLY_SORTIES", 45, aviation=1, fuel=0.25),
                    _primitive("GROUND_CONVOY", 60, vehicles=2, fuel=0.2),
                    _primitive("CONFIRM_RECEIPT", 5, comms=1),
                    _primitive("COORDINATE_DROP_ZONES", 15, comms=2, personnel=6),
                    _primitive("CONDUCT_AIR_DROP", 20, aviation=1, personnel=4),
                    _primitive("COORDINATE_GROUND_RECEPTION", 14, personnel=8),
                    _primitive("IMPLEMENT_ALTERNATE_DELIVERY", 18, logistics=2),
                ]),
                ("Quality_Assurance", [
                    _primitive("INSPECT_DELIVERED_SUPPLIES", 12, personnel=4),
                    _primitive("VERIFY_QUANTITY_AND_QUALITY", 10, logistics=1),
                    _primitive("DOCUMENT_DELIVERY_ISSUES", 8, personnel=2),
                    _primitive("COORDINATE_INVENTORY", 14, logistics=2),
                ]),
                ("Return_Operations", [
                    _primitive("PREPARE_RETURN_LOAD", 12, logistics=1),
                    _primitive("COORDINATE_RETURN_LOGISTICS", 16, logistics=2),
                    _primitive("IMPLEMENT_MAINTENANCE_CHECKS", 14, aviation=2),
                    _primitive("DOCUMENT_RETURN_CARGO", 10, logistics=1),
                ]),
            ]),
            ("Maintenance_Support", [
                ("Aircraft_Maintenance", [
                    _primitive("CONDUCT_PREFLIGHT_INSPECTION", 12, aviation=2),
                    _primitive("PERFORM_LINE_MAINTENANCE", 20, aviation=3),
                    _primitive("TROUBLESHOOT_SYSTEM_ISSUES", 16, aviation=2),
                    _primitive("REPLACE_CRITICAL_COMPONENTS", 18, aviation=2),
                ]),
                ("Ground_Support", [
                    _primitive("MAINTAIN_GROUND_EQUIPMENT", 14, logistics=2),
                    _primitive("COORDINATE_REFUELING", 10, aviation=1),
                    _primitive("PROVIDE_GROUND_POWER", 8, logistics=1),
                    _primitive("SUPPORT_AIRCRAFT_TURNAROUND", 12, personnel=6),
                ]),
            ]),
            ("Emergency_Procedures", [
                ("Contingency_Planning", [
                    _primitive("DEVELOP_EMERGENCY_PLANS", 16, personnel=6),
                    _primitive("PREPARE_DIVERSION_ROUTES", 14, gis=2),
                    _primitive("COORDINATE_EMERGENCY_RESOURCES", 12, comms=2),
                    _primitive("DRILL_EMERGENCY_PROCEDURES", 20, personnel=10),
                ]),
                ("Incident_Response", [
                    _primitive("RESPOND_TO_EMERGENCY", 8, personnel=8),
                    _primitive("COORDINATE_RESCUE_OPERATIONS", 15, comms=2),
                    _primitive("IMPLEMENT_DAMAGE_CONTROL", 18, personnel=12),
                    _primitive("EXECUTE_EVACUATION_PLAN", 22, personnel=10, vehicles=2),
                ]),
            ]),
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
