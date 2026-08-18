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
        
        # Extract threat assessments from validation if not provided
        threats = threat_assessments or recommended.validation.get("threat_assessments", [])
        confidence = min(.95, max(.1, .55 + .05 * len(recommended.cbr_matches) - .02 * len(recommended.validation["rule_firings"])))
        
        reasons = ["It has the highest risk-adjusted utility score.", f"Its estimated duration is {recommended.estimated_duration_min} minutes.", "It passed the applicable hard doctrine and ROE checks."]
        
        max_threat_risk = recommended.validation.get("max_threat_risk", 0.2)
        if max_threat_risk > 0.5:
            reasons.append(f"Favored cautious posture due to high assessed threat risk ({max_threat_risk * 100:.1f}%).")
        elif max_threat_risk > 0.2:
            reasons.append(f"Balanced posture selected matching moderate threat risk ({max_threat_risk * 100:.1f}%).")
        else:
            reasons.append(f"Bold posture favored due to low threat risk environment ({max_threat_risk * 100:.1f}%).")
            
        if recommended.validation.get("aco_score") is not None:
            reasons.append(f"Resource allocation optimized via ACO (Score: {recommended.validation['aco_score']:.2f}).")
            
        supporting_evidence = []
        for t in threats:
            supporting_evidence.append({
                "source": "Bayesian Threat Network",
                "threat_type": t.get("threat_type"),
                "probability": t.get("probability"),
                "risk_score": t.get("risk_score"),
                "confidence": t.get("confidence")
            })
            
        if recommended.validation.get("aco_score") is not None:
            supporting_evidence.append({
                "source": "ACO Constraint Solver",
                "score": recommended.validation["aco_score"],
                "fuel_used": recommended.validation["aco_fuel_used"],
                "resource_used": recommended.validation["aco_resource_used"],
                "assignments_count": len(recommended.validation["aco_assignments"])
            })

        # Append wargame simulation results if available
        sim_score = recommended.validation.get("simulation_score")
        if sim_score:
            reasons.append(f"Wargame Rank Rationale: {sim_score.get('ranking_rationale')}")
            for line in sim_score.get("explanation", []):
                supporting_evidence.append({
                    "source": "Wargame Simulation",
                    "detail": line.strip()
                })

        return Explanation(
            decision=f"{recommended.name} is recommended; commander authorisation remains required.",
            primary_reasons=reasons,
            supporting_evidence=supporting_evidence,
            rule_firings=recommended.validation["rule_firings"], cbr_matches=recommended.cbr_matches,
            risk_factors=["Threat estimates remain probabilistic.", "Operational conditions may change after planning."],
            alternatives=alternatives, confidence=round(confidence, 2),
            uncertainty_sources=["Sensor quality", "Weather forecast confidence", "Historical-case transferability"],
        )

