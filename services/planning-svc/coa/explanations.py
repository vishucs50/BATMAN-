from __future__ import annotations

from dataclasses import asdict, dataclass

from .generator import COA


@dataclass
class Explanation:
    decision: str
    primary_reasons: list[str]
    supporting_evidence: list[dict]
    rule_firings: list[str]
    cbr_matches: list[str]
    risk_factors: list[str]
    alternatives: list[dict]
    confidence: float
    uncertainty_sources: list[str]
    model_version: str = "phase1-symbolic-1.0"

    def as_dict(self) -> dict:
        return asdict(self)


class ExplanationGenerator:
    def generate(self, coas: list[COA], threat_assessments: list[dict] | None = None) -> Explanation:
        if not coas:
            raise ValueError("at least one COA is required")
        recommended = max(coas, key=lambda item: item.utility_score)
        alternatives = [{"name": coa.name, "utility_score": coa.utility_score, "why_lower": "Lower risk-adjusted utility"} for coa in coas if coa.id != recommended.id]
        threats = threat_assessments or []
        confidence = min(.95, max(.1, .55 + .05 * len(recommended.cbr_matches) - .02 * len(recommended.validation["rule_firings"])))
        return Explanation(
            decision=f"{recommended.name} is recommended; commander authorisation remains required.",
            primary_reasons=["It has the highest risk-adjusted utility score.", f"Its estimated duration is {recommended.estimated_duration_min} minutes.", "It passed the applicable hard doctrine and ROE checks."],
            supporting_evidence=threats,
            rule_firings=recommended.validation["rule_firings"], cbr_matches=recommended.cbr_matches,
            risk_factors=["Threat estimates remain probabilistic.", "Operational conditions may change after planning."],
            alternatives=alternatives, confidence=round(confidence, 2),
            uncertainty_sources=["Sensor quality", "Weather forecast confidence", "Historical-case transferability"],
        )
