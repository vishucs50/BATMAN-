from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from cbr.engine import Case, CaseBasedReasoner
from htn.models import WorldState
from htn.planner import HTNPlanner
from rules.engine import RuleEngine


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
        for style, modifier in self.styles.items():
            plan = self.planner.plan(mission_type, state)
            resources: dict[str, float] = {}
            for task in plan.executable_tasks:
                for resource, amount in task.required_resources.items():
                    resources[resource] = resources.get(resource, 0) + amount
            duration = max(1, round(plan.estimated_duration_min * modifier["duration"]))
            validation = self.rule_engine.validate_plan(state, plan.executable_tasks)
            # Simple architecture utility: success/risk, time, resource efficiency, ROE.
            utility = round((.35 * modifier["risk"]) + (.15 * (1 / modifier["duration"])) + (.10 * (1 / (1 + sum(resources.values()) / 100))) + (.04 if validation["valid"] else 0) - validation["soft_penalty"] / 100, 4)
            result.append(COA(str(uuid4()), f"{mission_type.replace('_', ' ').title()} — {style.title()}", style, plan.hierarchy.as_dict(), duration, resources, [modifier["assumption"], "Commander approval is required before execution."], utility, [case.id for case, _score in matches], validation))
        return sorted(result, key=lambda coa: coa.utility_score, reverse=True)
