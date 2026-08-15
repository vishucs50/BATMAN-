"""
Transparent, risk-adjusted COA utility scoring.

Implements the seven-factor utility function from BATMAN_Architecture.md §8.3:

  U(COA) = Σ wᵢ × normalised_component(i)  −  variance_penalty

where:
  w_success       = 0.35
  w_casualties    = 0.25
  w_time          = 0.15
  w_resources     = 0.10
  w_risk          = 0.08
  w_roe           = 0.04
  w_flexibility   = 0.03

Every COAScore includes a structured explanation so that the commander
understands exactly why one COA is ranked above another.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .statistics import OutcomeStatistics


# ── Score output ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class ComponentScore:
    """One factor contribution to the final utility score."""
    name: str
    raw_value: float
    normalised: float
    weight: float
    contribution: float
    explanation: str


@dataclass(frozen=True)
class COAScore:
    """
    Full transparent COA utility score.

    Includes component-level breakdown so the commander understands
    the precise trade-offs (e.g., COA-B is 12% safer but takes 40 min longer).
    """

    coa_id: str
    utility_score: float
    risk_score: float
    mission_effectiveness: float
    resource_efficiency: float
    roe_compliance: float
    flexibility: float

    component_scores: tuple[ComponentScore, ...]
    explanation: list[str]
    ranking_rationale: str


# ── Scoring engine ────────────────────────────────────────────────────────────
class COAScoringEngine:
    """
    Computes a fully explained utility score from Monte Carlo outcome statistics.

    Weights follow the architecture specification and can be overridden per-call
    for scenario-specific trade-offs (e.g., humanitarian operations prioritise
    ROE compliance over speed).
    """

    default_weights: dict[str, float] = {
        "success":     0.35,
        "casualties":  0.25,
        "time":        0.15,
        "resources":   0.10,
        "risk":        0.08,
        "roe":         0.04,
        "flexibility": 0.03,
    }

    def score(
        self,
        coa: Any,
        statistics: OutcomeStatistics,
        threat_probability: float = 0.0,
        constraint_penalty: float = 0.0,
        weights: dict[str, float] | None = None,
    ) -> COAScore:
        """
        Score a single COA from its Monte Carlo statistics.

        Parameters
        ----------
        coa:                COA dataclass or dict (must have estimated_duration_min).
        statistics:         Aggregated Monte Carlo outcome distributions.
        threat_probability: Mission-level threat probability (from ThreatAssessment).
        constraint_penalty: Additional penalty from hard constraint violations.
        weights:            Override the default architecture weights.
        """
        w = {**self.default_weights, **(weights or {})}
        declared_duration = max(getattr(coa, "estimated_duration_min", 1) or 1, 1)

        # ── Component metrics (all normalised to [0, 1]) ──────────────────────

        # 1. Mission effectiveness = success rate + objective completion.
        mission_effectiveness = min(
            1.0,
            statistics.mission_success_rate * 0.7
            + statistics.objective_completion_rate * 0.3,
        )

        # 2. Casualty avoidance (inverse of expected casualties, penalised by variance).
        max_expected = max(statistics.expected_friendly_casualties, 0.001)
        casualty_avoidance = 1.0 / (1.0 + max_expected)
        # Penalise high variance in casualties (unpredictable = higher risk).
        variance_correction = min(
            0.25,
            statistics.casualty_stddev / (1.0 + max_expected) * 0.3,
        )
        casualty_component = max(0.0, casualty_avoidance - variance_correction)

        # 3. Time efficiency.
        p50_time = statistics.completion_time_quantiles.get("p50", declared_duration)
        time_component = 1.0 / (1.0 + max(0.0, p50_time - declared_duration) / declared_duration)

        # 4. Resource efficiency (fuel × ammo balance).
        fuel_efficiency = 1.0 / (1.0 + statistics.expected_fuel_usage)
        ammo_efficiency = 1.0 / (1.0 + statistics.expected_ammo_usage)
        resource_efficiency = (fuel_efficiency + ammo_efficiency) / 2.0

        # 5. Risk score (threat + violation + casualty dispersion).
        risk_from_threat = threat_probability * 0.4
        risk_from_violations = statistics.constraint_violation_rate * 0.3
        risk_from_dispersion = min(0.3, statistics.casualty_stddev / (1.0 + max_expected) * 0.3)
        risk_score = min(1.0, risk_from_threat + risk_from_violations + risk_from_dispersion)
        risk_component = 1.0 - risk_score

        # 6. ROE compliance.
        roe_compliance = max(0.0, 1.0 - statistics.roe_violation_rate)
        civilian_penalty = statistics.civilian_casualty_rate * 0.5
        roe_component = max(0.0, roe_compliance - civilian_penalty)

        # 7. Flexibility (fewer distinct failure modes = more robust COA).
        flexibility = 1.0 / (1.0 + len(statistics.failure_mode_frequency))

        # ── Weighted utility ──────────────────────────────────────────────────
        raw_utility = (
            w["success"]     * mission_effectiveness
            + w["casualties"]  * casualty_component
            + w["time"]        * time_component
            + w["resources"]   * resource_efficiency
            + w["risk"]        * risk_component
            + w["roe"]         * roe_component
            + w["flexibility"] * flexibility
            - constraint_penalty
        )

        # Variance penalty: penalise unpredictability (σ/μ of casualties).
        cv = statistics.casualty_stddev / max(mission_effectiveness, 0.01)
        variance_penalty = min(0.15, cv * 0.1)
        utility = max(0.0, raw_utility - variance_penalty)

        # ── Component breakdown ───────────────────────────────────────────────
        components = (
            ComponentScore("Mission Effectiveness", statistics.mission_success_rate, mission_effectiveness, w["success"], round(w["success"] * mission_effectiveness, 4), f"Success rate {statistics.mission_success_rate:.1%}, objective completion {statistics.objective_completion_rate:.1%}"),
            ComponentScore("Casualty Avoidance", statistics.expected_friendly_casualties, casualty_component, w["casualties"], round(w["casualties"] * casualty_component, 4), f"Expected {statistics.expected_friendly_casualties:.2f} casualties ± {statistics.casualty_stddev:.2f}"),
            ComponentScore("Time Efficiency", p50_time, time_component, w["time"], round(w["time"] * time_component, 4), f"Median completion {p50_time:.0f} min vs declared {declared_duration} min"),
            ComponentScore("Resource Efficiency", statistics.expected_fuel_usage, resource_efficiency, w["resources"], round(w["resources"] * resource_efficiency, 4), f"Expected fuel {statistics.expected_fuel_usage:.3f}, ammo {statistics.expected_ammo_usage:.3f}"),
            ComponentScore("Risk", risk_score, risk_component, w["risk"], round(w["risk"] * risk_component, 4), f"Risk={risk_score:.2f} (threat={risk_from_threat:.2f}, violations={risk_from_violations:.2f})"),
            ComponentScore("ROE Compliance", statistics.roe_violation_rate, roe_component, w["roe"], round(w["roe"] * roe_component, 4), f"ROE violation rate {statistics.roe_violation_rate:.1%}, civilian casualty rate {statistics.civilian_casualty_rate:.1%}"),
            ComponentScore("Flexibility", len(statistics.failure_mode_frequency), flexibility, w["flexibility"], round(w["flexibility"] * flexibility, 4), f"{len(statistics.failure_mode_frequency)} distinct failure modes observed"),
        )

        # ── Plain-language explanation ─────────────────────────────────────────
        coa_name = getattr(coa, "coa_id", getattr(coa, "name", "COA"))
        explanation = [
            f"[{coa_name}] Utility: {utility:.4f} over {statistics.run_count} Monte Carlo runs.",
            f"  → Success probability: {statistics.mission_success_rate:.1%}",
            f"  → Median completion time: {p50_time:.0f} min (P95: {statistics.completion_time_quantiles.get('p95', 0):.0f} min)",
            f"  → Expected casualties: {statistics.expected_friendly_casualties:.2f} ± {statistics.casualty_stddev:.2f}",
            f"  → Fuel consumption: {statistics.expected_fuel_usage:.3f} (±{statistics.fuel_usage_stddev:.3f})",
            f"  → ROE violation rate: {statistics.roe_violation_rate:.1%}",
            f"  → Risk score: {risk_score:.2f}",
            f"  → Constraint violation rate: {statistics.constraint_violation_rate:.1%}",
        ]
        if statistics.failure_mode_frequency:
            top = list(statistics.failure_mode_frequency.items())[:3]
            explanation.append(
                "  → Top failure modes: " + ", ".join(f"{m}({c})" for m, c in top)
            )
        if statistics.failure_mode_variance_contribution:
            top_var = list(statistics.failure_mode_variance_contribution.items())[:2]
            explanation.append(
                "  → Key variance drivers: " + ", ".join(f"{m}({v:.0%})" for m, v in top_var)
            )

        ranking_rationale = (
            f"Utility {utility:.4f} = "
            + " + ".join(f"{c.contribution:.3f}({c.name})" for c in components)
            + f" − {variance_penalty:.4f}(variance)"
        )

        return COAScore(
            coa_id=coa_name,
            utility_score=round(utility, 4),
            risk_score=round(risk_score, 4),
            mission_effectiveness=round(mission_effectiveness, 4),
            resource_efficiency=round(resource_efficiency, 4),
            roe_compliance=round(roe_component, 4),
            flexibility=round(flexibility, 4),
            component_scores=components,
            explanation=explanation,
            ranking_rationale=ranking_rationale,
        )

    def rank(
        self,
        entries: list[tuple[Any, OutcomeStatistics, float, float]],
    ) -> list[COAScore]:
        """
        Score and rank a set of COAs in descending utility order.

        Each entry is a tuple: (coa, statistics, threat_probability, constraint_penalty).
        """
        scores = [
            self.score(coa, stats, threat, penalty)
            for coa, stats, threat, penalty in entries
        ]
        return sorted(scores, key=lambda s: s.utility_score, reverse=True)
