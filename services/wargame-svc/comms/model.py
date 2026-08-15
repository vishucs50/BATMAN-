"""Simplified but explicit RF propagation and link reliability model."""
from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class CommunicationResult:
    """Quality and delivery outcome of one simulated communications attempt."""

    delivered: bool
    quality: float
    factors: dict[str, float]


class CommunicationModel:
    """Evaluates a link from range, terrain obstruction, weather, and EW effects."""

    def __init__(self, nominal_range_km: float = 25.0):
        if nominal_range_km <= 0:
            raise ValueError("nominal_range_km must be positive")
        self.nominal_range_km = nominal_range_km

    def transmit(self, baseline_quality: float, distance_km: float, terrain_obstruction: float, weather_quality: float, ew_interference: float, rng: random.Random) -> CommunicationResult:
        """Sample delivery without altering agents or the simulation state."""
        range_factor = max(.05, 1 - distance_km / self.nominal_range_km)
        obstruction_factor = max(.05, 1 - terrain_obstruction)
        ew_factor = max(.05, 1 - ew_interference)
        quality = min(1.0, max(0.0, baseline_quality * range_factor * obstruction_factor * weather_quality * ew_factor))
        return CommunicationResult(rng.random() < quality, quality, {"baseline": baseline_quality, "range_factor": range_factor, "terrain_obstruction": terrain_obstruction, "weather_quality": weather_quality, "ew_interference": ew_interference})
