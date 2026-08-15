"""Typed boundary objects for the Phase 2 simulation service."""
from __future__ import annotations

from dataclasses import dataclass

from shared.contracts import Mission, SimulationResult, WorldState


@dataclass(frozen=True)
class SimulationConfig:
    """Run controls injected into an individual simulation."""

    tick_minutes: int = 5
    max_duration_minutes: int = 480
    random_seed: int | None = None
    friendly_count: int = 3
    threat_count: int = 1
    civilian_count: int = 2
