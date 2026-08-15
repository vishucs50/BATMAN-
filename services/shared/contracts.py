"""Shared typed contracts that keep planning, assessment, and simulation decoupled.

This module is the single source of truth for all canonical data types shared
across service boundaries. Every Phase 1 and Phase 2 module imports from here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ObjectiveState(str, Enum):
    """Lifecycle state for a mission objective."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    ACHIEVED = "ACHIEVED"
    FAILED = "FAILED"


class SimulationEventType(str, Enum):
    """The event vocabulary exchanged by the simulation dispatcher."""
    MOVEMENT = "MOVEMENT"
    FUEL = "FUEL"
    DETECTION = "DETECTION"
    ENGAGEMENT = "ENGAGEMENT"
    COMMUNICATION = "COMMUNICATION"
    LOGISTICS = "LOGISTICS"
    OBJECTIVE = "OBJECTIVE"
    WEATHER = "WEATHER"
    MISSION_END = "MISSION_END"


@dataclass(frozen=True)
class Mission:
    """Canonical mission projection shared across service boundaries."""
    mission_id: str
    mission_type: str
    objectives: tuple[str, ...] = ()
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldState:
    """
    Portable battlefield-world inputs consumed by planning and simulation.

    Represents the mission-level context: terrain characteristics, weather,
    threat level, logistics state, and comms baseline. Immutable once passed
    into a simulation run; the simulation uses LiveWorldState internally.
    """
    terrain: str = "PLAINS"
    elevation_m: float = 0.0
    slope_degrees: float = 0.0
    trafficability: float = 1.0
    vegetation_density: float = 0.0
    initial_weather: str = "CLEAR"
    threat_probability: float = 0.2
    civilian_density: float = 0.1
    comms_baseline: float = 0.95
    fuel_available: float = 1.0
    ammunition_available: float = 1.0


@dataclass
class SimulationState:
    """Mutable run-local state, isolated from the canonical input world state."""
    time_min: float = 0.0
    objectives_completed: int = 0
    constraint_violations: list[str] = field(default_factory=list)
    event_log: list[dict[str, Any]] = field(default_factory=list)
    terminated: bool = False


@dataclass(frozen=True)
class SimulationEvent:
    """A scheduled simulation event with deterministic ordering metadata."""
    event_type: SimulationEventType
    time_min: float
    sequence: int
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Canonical mutable battlefield-agent state."""
    position: tuple[int, int] = (0, 0)
    status: str = "ACTIVE"
    health: float = 1.0
    resources: dict[str, float] = field(default_factory=lambda: {"fuel": 1.0, "ammo": 1.0})
    visibility: float = 1.0
    decision_state: str = "IDLE"


@dataclass(frozen=True)
class COA:
    """
    Service-neutral COA representation.

    Phase 1 planner outputs are structurally adapted to this contract before
    being consumed by the Phase 2 simulation engine.
    """
    coa_id: str
    task_hierarchy: dict[str, Any]
    estimated_duration_min: int
    required_resources: dict[str, float] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ThreatAssessment:
    """Canonical assessment passed from the threat service to consumers."""
    threat_type: str
    probability: float
    confidence: float
    risk_score: float
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Canonical result emitted by an individual simulation execution."""
    mission_id: str
    success: bool
    termination_reason: str
    completion_time_min: float
    friendly_casualties: int
    civilian_casualties: int
    fuel_consumed: float
    communication_failures: int
    constraint_violations: list[str]
    objectives_completed: int
    objectives_total: int
    failure_modes: list[str]
    event_log: list[dict[str, Any]]
    weather_history: list[str]
    # Extended fields for Phase 2 full-fidelity logging.
    ammo_consumed: float = 0.0
    roe_violations: int = 0
