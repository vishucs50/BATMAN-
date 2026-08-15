from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

try:
    from pgmpy.factors.discrete import TabularCPD
    from pgmpy.inference import VariableElimination
    from pgmpy.models import BayesianNetwork
except ImportError:  # pragma: no cover - exercised where pgmpy is unavailable
    BayesianNetwork = None


@dataclass
class ThreatAssessment:
    threat_type: str
    probability: float
    confidence: float
    risk_score: float
    evidence: dict[str, Any]
    bayesian_params: dict[str, Any]
    countermeasures: list[str]
    assessed_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ThreatNetwork:
    """pgmpy-backed threat estimator for infiltration, ambush, and IED risk."""

    profiles = {
        "INFILTRATION": (0.16, ["QRT_DEPLOYMENT", "AERIAL_SURVEILLANCE", "CORDON_ESTABLISHMENT"]),
        "AMBUSH": (0.13, ["AVOID_NATURAL_CHOKE_POINTS", "INCREASE_LEAD_ELEMENT_STANDOFF", "ALTERNATE_ROUTE"]),
        "IED": (0.11, ["ROUTE_DEVIATION", "EOD_PRE_CLEARANCE", "MRAP_ASSIGNMENT"]),
    }

    def __init__(self, threat_type: str):
        if threat_type not in self.profiles:
            raise ValueError(f"unsupported threat type: {threat_type}")
        self.threat_type = threat_type
        self.model = self._build_model() if BayesianNetwork else None

    def _build_model(self):
        model = BayesianNetwork([("sensor_quality", "threat"), ("historical_pattern", "threat"), ("weather", "threat"), ("time_of_day", "threat")])
        # Evidence is binary. CPD values deliberately remain inspectable and versionable.
        model.add_cpds(
            TabularCPD("sensor_quality", 2, [[.45], [.55]]), TabularCPD("historical_pattern", 2, [[.55], [.45]]),
            TabularCPD("weather", 2, [[.50], [.50]]), TabularCPD("time_of_day", 2, [[.50], [.50]]),
            TabularCPD("threat", 2, [[.92, .82, .82, .68, .82, .68, .68, .45, .82, .68, .68, .45, .68, .45, .45, .25], [.08, .18, .18, .32, .18, .32, .32, .55, .18, .32, .32, .55, .32, .55, .55, .75]], evidence=["sensor_quality", "historical_pattern", "weather", "time_of_day"], evidence_card=[2, 2, 2, 2]),
        )
        model.check_model()
        return model

    def assess(self, evidence: dict[str, Any]) -> ThreatAssessment:
        values = {key: int(bool(evidence.get(key, False))) for key in ("sensor_quality", "historical_pattern", "weather", "time_of_day")}
        prior, countermeasures = self.profiles[self.threat_type]
        if self.model:
            posterior = float(VariableElimination(self.model).query(["threat"], evidence=values, show_progress=False).values[1])
        else:
            # Bayes-compatible likelihood fallback for constrained deployments.
            likelihood = sum(values.values()) / 4
            posterior = (prior * (.25 + .75 * likelihood)) / max(prior * (.25 + .75 * likelihood) + (1 - prior) * (1 - .45 * likelihood), 1e-9)
        confidence = round(.45 + .12 * sum(values.values()), 2)
        risk = round(min(10.0, posterior * 10 * confidence), 2)
        return ThreatAssessment(self.threat_type, round(posterior, 4), min(confidence, .95), risk, evidence, {"prior": prior, "posterior": round(posterior, 4), "evidence_states": values}, countermeasures, datetime.now(timezone.utc).isoformat())
