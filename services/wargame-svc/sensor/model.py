"""Probabilistic sensor surface independent of the simulation scheduler."""
from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class DetectionResult:
    """A traceable sensor-detection decision for one target observation."""

    detected: bool
    probability: float
    factors: dict[str, float]


class SensorModel:
    """Computes weather, terrain, and distance adjusted detection probability."""

    def __init__(self, base_effectiveness: float = 0.8, maximum_range_km: float = 8.0):
        if not 0 < base_effectiveness <= 1 or maximum_range_km <= 0:
            raise ValueError("sensor parameters must be positive probabilities and ranges")
        self.base_effectiveness = base_effectiveness
        self.maximum_range_km = maximum_range_km

    def detect(self, distance_km: float, weather_effectiveness: float, terrain_cover: float, rng: random.Random) -> DetectionResult:
        """Sample detection and retain each contributor for audit/explainability."""
        range_factor = max(0.0, 1 - distance_km / self.maximum_range_km)
        cover_factor = max(0.05, 1 - terrain_cover)
        probability = min(1.0, self.base_effectiveness * range_factor * weather_effectiveness * cover_factor)
        return DetectionResult(rng.random() < probability, probability, {"base_effectiveness": self.base_effectiveness, "range_factor": range_factor, "weather_effectiveness": weather_effectiveness, "cover_factor": cover_factor})
