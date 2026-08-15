from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

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
        vector = self.encode(case)
        self.cases.append(case)
        self._vectors.append(vector)
        if self._index:
            self._index.add(vector.reshape(1, -1))

    @classmethod
    def synthetic_seed_cases(cls, count: int = 200) -> list[Case]:
        mission_types = ["COUNTER_INFILTRATION", "COUNTER_TERRORISM", "HIGH_ALTITUDE_LOGISTICS"]
        terrains = ["FORESTED", "URBAN", "HIGH_ALTITUDE", "MOUNTAINOUS"]
        threats = ["INFILTRATION", "AMBUSH", "IED"]
        return [Case(
            id=f"SYN-{index:03d}", mission_type=mission_types[index % 3], terrain=terrains[index % 4],
            threat=threats[index % 3], resources=.45 + (index % 50) / 100,
            urgency=.3 + (index % 60) / 100, outcome="SUCCESS" if index % 5 else "PARTIAL",
            plan_skeleton={"style": ("BOLD", "BALANCED", "CAUTIOUS")[index % 3]},
            lessons_learned=["Synthetic academic seed case"],
        ) for index in range(count)]
