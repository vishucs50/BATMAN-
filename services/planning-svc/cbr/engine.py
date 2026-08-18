from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any
import random

try:  # FAISS is the production index; the fallback preserves offline tests.
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - environment dependent
    faiss = None

import numpy as np


@dataclass
class Case:
    id: str
    mission_type: str
    terrain: str
    threat: str
    resources: float
    urgency: float
    outcome: str
    plan_skeleton: dict[str, Any] = field(default_factory=dict)
    lessons_learned: list[str] = field(default_factory=list)


class CaseBasedReasoner:
    """Retrieve → reuse → revise → retain mission-memory cycle."""

    dimension = 8

    def __init__(self) -> None:
        self.cases: list[Case] = []
        self._index = faiss.IndexFlatIP(self.dimension) if faiss else None
        self._vectors: list[np.ndarray] = []

    @staticmethod
    def _bucket(value: str) -> float:
        return int(sha256(value.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

    def encode(self, case: Case) -> np.ndarray:
        vector = np.array([
            self._bucket(case.mission_type), self._bucket(case.terrain), self._bucket(case.threat),
            min(max(case.resources, 0), 1), min(max(case.urgency, 0), 1),
            1.0 if case.outcome == "SUCCESS" else .5 if case.outcome == "PARTIAL" else 0.0,
            self._bucket(case.plan_skeleton.get("style", "BALANCED")), 1.0,
        ], dtype="float32")
        return vector / max(float(np.linalg.norm(vector)), 1e-9)

    def index(self, cases: list[Case]) -> None:
        self.cases = []
        self._vectors = []
        self._index = faiss.IndexFlatIP(self.dimension) if faiss else None
        for case in cases:
            self.retain(case)

    def retrieve(self, query: Case, k: int = 5) -> list[tuple[Case, float]]:
        if not self.cases:
            return []
        vector = self.encode(query)
        if self._index:
            scores, indices = self._index.search(vector.reshape(1, -1), min(k, len(self.cases)))
            return [(self.cases[int(index)], float(score)) for score, index in zip(scores[0], indices[0]) if index >= 0]
        scores = [float(np.dot(vector, stored)) for stored in self._vectors]
        return sorted(zip(self.cases, scores), key=lambda item: item[1], reverse=True)[:k]

    def reuse(self, query: Case, match: Case) -> dict[str, Any]:
        """Adapt only the safe, declarative plan skeleton; HTN still validates it."""
        return {**match.plan_skeleton, "mission_type": query.mission_type, "adapted_from": match.id}

    def revise(self, plan: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
        revised = dict(plan)
        revised["validation"] = validation
        revised["requires_replan"] = not validation.get("valid", False)
        return revised

    def retain(self, case: Case) -> None:
        # Prevent duplicates
        if any(c.id == case.id for c in self.cases):
            return
            
        vector = self.encode(case)
        self.cases.append(case)
        self._vectors.append(vector)
        if self._index:
            self._index.add(vector.reshape(1, -1))

    def save_index(self, filepath: str) -> None:
        import json
        import os
        from dataclasses import asdict
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            for case in self.cases:
                # Do not persist synthetic seed cases, only real simulations
                if case.id.startswith("SYN-"):
                    continue
                f.write(json.dumps(asdict(case)) + "\n")

    def load_index(self, filepath: str) -> None:
        import json
        import os
        if not os.path.exists(filepath):
            return
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                self.retain(Case(**data))

    @classmethod
    def synthetic_seed_cases(cls, count: int = 3000) -> list[Case]:
        random.seed(42)  # Fixed seed for reproducibility
        
        mission_types = ["COUNTER_INFILTRATION", "COUNTER_TERRORISM", "HIGH_ALTITUDE_LOGISTICS"]
        terrains = ["FORESTED", "URBAN", "HIGH_ALTITUDE", "MOUNTAINOUS", "DESERT", "JUNGLE", "URBAN_SPRAWL", "COASTAL"]
        threats = ["INFILTRATION", "AMBUSH", "IED", "SNIPER", "GUERILLA", "TERRORIST_CELL", "SABOTAGE", "ASSAULT"]
        outcomes = ["SUCCESS", "PARTIAL", "FAILURE"]
        styles = ["BOLD", "BALANCED", "CAUTIOUS", "AGGRESSIVE", "DEFENSIVE", "MOBILE", "STATIC", "HYBRID"]
        
        # Expanded lesson learned templates
        lesson_templates = [
            "Synthetic academic seed case", "Early warning system critical", "Terrain advantage exploited",
            "Communication breakdown avoided", "Resource allocation optimized", "Surprise element crucial",
            "Coordination with ground forces essential", "Weather conditions impacted operation",
            "Additional reconnaissance needed", "Force protection measures effective",
            "Logistics chain vulnerability identified", "Civilian interference mitigated",
            "Equipment reliability issues noted", "Night vision capabilities inadequate",
            "Medical evacuation procedures needed improvement", "Intelligence accuracy concerns",
            "Fire support coordination successful", "Counter-IED measures effective",
            "Psychological operations impactful", "Local population engagement positive",
            "Communications jamming effective", "Electronic warfare capabilities utilized",
            "Drone surveillance provided critical intel", "Alternative routes identified",
            "Hostage rescue protocols successful", "Building clearing tactics effective",
            "Crisis negotiation strategies successful", "Evacuation procedures well-executed",
            "Decontamination procedures needed", "Chemical threat response tested",
            "Fuel management system implemented", "Maintenance schedule adjusted",
            "Aircraft availability constraints encountered", "Altitude effects on performance noted",
            "Weather window utilization optimal", "Supply distribution efficiency improved",
            "Civil-military cooperation enhanced", "Security sweep comprehensive",
            "Route reconnaissance thorough", "Rehearsals identified vulnerabilities",
            "Command and control structure effective", "Reserve forces deployment strategic",
            "Containment perimeter maintained", "Observation posts coverage adequate"
        ]
        
        cases = []
        for index in range(count):
            mission_type = random.choice(mission_types)
            terrain = random.choice(terrains)
            threat = random.choice(threats)
            
            # Generate varied and realistic resource levels
            resources = random.uniform(0.25, 0.95)
            
            # Urgency varies with mission type
            if mission_type == "COUNTER_TERRORISM":
                urgency = random.uniform(0.7, 0.98)  # Generally high urgency
            elif mission_type == "COUNTER_INFILTRATION":
                urgency = random.uniform(0.4, 0.9)
            else:  # Logistics
                urgency = random.uniform(0.2, 0.8)
            
            # Outcome influenced by resources and urgency
            outcome_roll = random.random()
            if resources > 0.7 and outcome_roll < 0.85:
                outcome = "SUCCESS"
            elif resources > 0.5 and outcome_roll < 0.7:
                outcome = "SUCCESS"
            elif resources > 0.3 and outcome_roll < 0.5:
                outcome = "PARTIAL"
            else:
                outcome = random.choice(outcomes)
            
            # Plan style with mission-specific preferences
            if mission_type == "COUNTER_TERRORISM":
                style_weights = {"BOLD": 0.4, "BALANCED": 0.3, "CAUTIOUS": 0.15, "AGGRESSIVE": 0.15}
            elif mission_type == "COUNTER_INFILTRATION":
                style_weights = {"BOLD": 0.2, "BALANCED": 0.3, "CAUTIOUS": 0.3, "DEFENSIVE": 0.2}
            else:  # Logistics
                style_weights = {"BOLD": 0.1, "BALANCED": 0.3, "CAUTIOUS": 0.4, "STATIC": 0.2}
            
            style = random.choices(
                list(style_weights.keys()),
                weights=list(style_weights.values())
            )[0]
            
            # Generate 2-5 lesson learned from templates
            num_lessons = random.randint(2, 5)
            selected_lessons = random.sample(lesson_templates, min(num_lessons, len(lesson_templates)))
            
            # Add some mission-specific plan elements
            plan_skeleton = {
                "style": style,
                "primary_objective": mission_type[:3] + str(random.randint(1, 10)),
            }
            
            if mission_type == "COUNTER_TERRORISM":
                plan_skeleton.update({
                    "entry_points": random.randint(1, 4),
                    "hostages": random.randint(1, 15),
                    "terrorists": random.randint(1, 8),
                    "civilians_present": random.choice([True, False]),
                    "requires_sniper": random.choice([True, False]),
                    "has_negotiation_team": random.choice([True, False]),
                })
            elif mission_type == "COUNTER_INFILTRATION":
                plan_skeleton.update({
                    "grid_squares": random.randint(4, 25),
                    "sensor_network": random.choice(["ACOUSTIC", "SEISMIC", "THERMAL", "RADAR", "DRONE"]),
                    "cordon_type": random.choice(["STATIC", "DYNAMIC", "MIXED"]),
                    "night_ops": random.choice([True, False]),
                    "has_air_support": random.choice([True, False]),
                })
            else:  # HIGH_ALTITUDE_LOGISTICS
                plan_skeleton.update({
                    "altitude_m": random.randint(2000, 7000),
                    "payload_kg": random.randint(1000, 15000),
                    "aircraft_type": random.choice(["C-130", "CH-47", "UH-60", "C-17", "MI-8"]),
                    "sorties": random.randint(1, 12),
                    "requires_airdrop": random.choice([True, False]),
                    "weather_confidence": random.uniform(0.3, 0.9),
                })
            
            case = Case(
                id=f"SYN-{index:04d}",
                mission_type=mission_type,
                terrain=terrain,
                threat=threat,
                resources=resources,
                urgency=urgency,
                outcome=outcome,
                plan_skeleton=plan_skeleton,
                lessons_learned=selected_lessons,
            )
            cases.append(case)
        
        return cases
