"""Deterministic resource tracking used by the simulation engine."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogisticsResult:
    """Resource state after a consumption event and any breached reserves."""

    resources: dict[str, float]
    violations: tuple[str, ...]


class LogisticsModel:
    """Consumes fuel/ammunition and checks configurable minimum reserves."""

    def __init__(self, minimum_fuel_reserve: float = .2, minimum_ammo_reserve: float = .1):
        self.minimum_fuel_reserve = minimum_fuel_reserve
        self.minimum_ammo_reserve = minimum_ammo_reserve

    def consume(self, resources: dict[str, float], fuel: float = 0.0, ammunition: float = 0.0) -> LogisticsResult:
        """Return a new resource mapping; callers retain ownership of state mutation."""
        updated = dict(resources)
        updated["fuel"] = max(0.0, updated.get("fuel", 0.0) - fuel)
        updated["ammo"] = max(0.0, updated.get("ammo", 0.0) - ammunition)
        violations = []
        if updated["fuel"] < self.minimum_fuel_reserve:
            violations.append("FUEL_RESERVE")
        if updated["ammo"] < self.minimum_ammo_reserve:
            violations.append("AMMUNITION_RESERVE")
        return LogisticsResult(updated, tuple(violations))
