"""
Distribution-aware outcome statistics for the BATMAN Monte Carlo engine.

Produces full distributions (not just averages) for every outcome variable.
Also computes:
  • ROE violation rate (separate from general constraint violations)
  • Objective completion rate
  • Civilian casualty distribution
  • Sensitivity proxies (variance contribution per failure mode)
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import sqrt
from statistics import mean, stdev

from .models import SimulationResult


def _quantiles(values: list[float]) -> dict[str, float]:
    """Compute P05, P25, P50, P75, P95 over a sample."""
    if not values:
        return {"p05": 0.0, "p25": 0.0, "p50": 0.0, "p75": 0.0, "p95": 0.0}
    ordered = sorted(values)
    n = len(ordered)

    def pct(p: float) -> float:
        idx = round((n - 1) * p)
        return ordered[idx]

    return {
        "p05": pct(0.05),
        "p25": pct(0.25),
        "p50": pct(0.50),
        "p75": pct(0.75),
        "p95": pct(0.95),
    }


def _mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    m = mean(values)
    s = stdev(values) if len(values) > 1 else 0.0
    return round(m, 4), round(s, 4)


@dataclass(frozen=True)
class OutcomeStatistics:
    """
    Full distributional outcome aggregated over N independent simulation runs.

    Every field contains either a scalar probability/rate or a quantile dict
    so that commanders can reason about best-case, expected, and worst-case.
    """

    run_count: int

    # ── Success ───────────────────────────────────────────────────────────────
    mission_success_rate: float
    success_distribution: dict[bool, int]

    # ── Casualties ────────────────────────────────────────────────────────────
    expected_friendly_casualties: float
    casualty_stddev: float
    casualty_quantiles: dict[str, float]

    expected_civilian_casualties: float
    civilian_casualty_rate: float

    # ── Time ─────────────────────────────────────────────────────────────────
    completion_time_quantiles: dict[str, float]

    # ── Fuel & ammo ───────────────────────────────────────────────────────────
    expected_fuel_usage: float
    fuel_usage_stddev: float
    fuel_quantiles: dict[str, float]

    expected_ammo_usage: float
    ammo_usage_stddev: float

    # ── Communications ────────────────────────────────────────────────────────
    communication_failure_distribution: dict[int, int]
    expected_comms_failures: float

    # ── Constraints & ROE ─────────────────────────────────────────────────────
    constraint_violation_rate: float
    roe_violation_rate: float
    objective_completion_rate: float

    # ── Failure modes ─────────────────────────────────────────────────────────
    failure_mode_frequency: dict[str, int]

    # ── Sensitivity proxies ───────────────────────────────────────────────────
    # Maps each failure mode to its proportional contribution to mission failure.
    failure_mode_variance_contribution: dict[str, float]


class OutcomeStatisticsEngine:
    """Aggregates a list of SimulationResult objects into full distributions."""

    def aggregate(self, results: list[SimulationResult]) -> OutcomeStatistics:
        if not results:
            raise ValueError("At least one SimulationResult is required")

        n = len(results)

        # ── Success ───────────────────────────────────────────────────────────
        success_counter = Counter(r.success for r in results)
        success_rate = success_counter[True] / n

        # ── Casualties ────────────────────────────────────────────────────────
        fc = [float(r.friendly_casualties) for r in results]
        cc = [float(r.civilian_casualties) for r in results]
        mean_fc, std_fc = _mean_std(fc)
        mean_cc, _ = _mean_std(cc)
        civilian_rate = sum(1 for r in results if r.civilian_casualties > 0) / n

        # ── Time ─────────────────────────────────────────────────────────────
        times = [r.completion_time_min for r in results]

        # ── Fuel & ammo ───────────────────────────────────────────────────────
        fuels = [r.fuel_consumed for r in results]
        ammos = [getattr(r, "ammo_consumed", 0.0) for r in results]
        mean_fuel, std_fuel = _mean_std(fuels)
        mean_ammo, std_ammo = _mean_std(ammos)

        # ── Comms ─────────────────────────────────────────────────────────────
        comms = [r.communication_failures for r in results]
        comms_dist = dict(Counter(comms))
        mean_comms, _ = _mean_std([float(c) for c in comms])

        # ── Constraints ───────────────────────────────────────────────────────
        violation_rate = sum(1 for r in results if r.constraint_violations) / n
        roe_rate = sum(
            1 for r in results
            if any("ROE" in v for v in r.constraint_violations)
        ) / n
        obj_rate = sum(
            r.objectives_completed / max(r.objectives_total, 1) for r in results
        ) / n

        # ── Failure modes ─────────────────────────────────────────────────────
        fm_counter = Counter(m for r in results for m in r.failure_modes)
        top_modes = dict(fm_counter.most_common(10))

        # Variance contribution: how much does each failure mode appear in failed runs?
        failed_runs = [r for r in results if not r.success]
        failed_fm = Counter(m for r in failed_runs for m in r.failure_modes)
        total_failed_modes = sum(failed_fm.values()) or 1
        variance_contribution = {
            mode: round(count / total_failed_modes, 4)
            for mode, count in failed_fm.most_common(10)
        }

        return OutcomeStatistics(
            run_count=n,
            mission_success_rate=round(success_rate, 4),
            success_distribution={bool(k): v for k, v in success_counter.items()},
            expected_friendly_casualties=mean_fc,
            casualty_stddev=std_fc,
            casualty_quantiles=_quantiles(fc),
            expected_civilian_casualties=mean_cc,
            civilian_casualty_rate=round(civilian_rate, 4),
            completion_time_quantiles=_quantiles(times),
            expected_fuel_usage=mean_fuel,
            fuel_usage_stddev=std_fuel,
            fuel_quantiles=_quantiles(fuels),
            expected_ammo_usage=mean_ammo,
            ammo_usage_stddev=std_ammo,
            communication_failure_distribution=comms_dist,
            expected_comms_failures=round(mean_comms, 2),
            constraint_violation_rate=round(violation_rate, 4),
            roe_violation_rate=round(roe_rate, 4),
            objective_completion_rate=round(obj_rate, 4),
            failure_mode_frequency=top_modes,
            failure_mode_variance_contribution=variance_contribution,
        )
