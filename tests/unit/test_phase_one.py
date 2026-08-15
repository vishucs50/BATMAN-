from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "services"), str(ROOT / "services" / "planning-svc"), str(ROOT / "services" / "threat-svc"), str(ROOT / "services" / "kg-svc")]

from cbr import CaseBasedReasoner
from coa import COAGenerator, ExplanationGenerator
from htn import HTNPlanner
from htn.mission_domains import build_phase_one_domain
from rules import RuleEngine, phase_one_rules
from bayesian import ThreatNetwork
from seed_graph import build_entities, build_relationships


def test_htn_decomposes_each_phase_one_profile():
    for mission_type in ("COUNTER_INFILTRATION", "COUNTER_TERRORISM", "HIGH_ALTITUDE_LOGISTICS"):
        planner = HTNPlanner(build_phase_one_domain(), RuleEngine(phase_one_rules()))
        plan = planner.plan(mission_type, __import__("htn").WorldState({"mission_type": mission_type}))
        assert plan.executable_tasks
        assert all(task.primitive for task in plan.executable_tasks)


def test_coa_pipeline_generates_three_distinct_valid_options():
    engine = RuleEngine(phase_one_rules())
    cbr = CaseBasedReasoner(); cbr.index(cbr.synthetic_seed_cases())
    generator = COAGenerator(HTNPlanner(build_phase_one_domain(), engine), engine, cbr)
    coas = generator.generate("COUNTER_INFILTRATION", {"terrain": "FORESTED", "cordon_depth_m": 500, "own_force": 12, "threat_strength": 3, "graduated_force": True})
    assert {coa.style for coa in coas} == {"BOLD", "BALANCED", "CAUTIOUS"}
    assert all(coa.validation["valid"] for coa in coas)
    assert ExplanationGenerator().generate(coas).confidence > 0


def test_threat_network_returns_structured_assessment():
    assessment = ThreatNetwork("IED").assess({"sensor_quality": True, "historical_pattern": True, "weather": False, "time_of_day": True})
    assert 0 <= assessment.probability <= 1
    assert assessment.countermeasures


def test_graph_seed_has_200_entities_and_relationships():
    entities = build_entities()
    assert len(entities) == 200
    assert len(build_relationships(entities)) >= 200
