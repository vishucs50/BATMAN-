"""
Structured Simulation Log Builder.

SimulationLogger collects the complete, rich log that each simulation run
produces. It is consumed by:
  • Statistics engine (aggregation)
  • COA scoring (explanation context)
  • Phase 4 training pipeline (dataset)
  • After Action Review (AAR replay)

The log is immutable once committed: append-only, never mutated in place.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AgentDecisionRecord:
    """A single agent decision for the structured log."""

    time_min: float
    agent_id: str
    agent_type: str
    decision: str
    behaviour: str
    position: tuple[int, int]
    health: float
    fuel: float
    ammo: float


@dataclass
class SimulationLog:
    """
    Complete record of one simulation run, structured for learning and replay.

    Produced by SimulationLogger; consumed by statistics, scoring, and AAR.
    """

    # ── Identity ─────────────────────────────────────────────────────────────
    mission_id: str
    coa_id: str
    run_seed: int

    # ── Configuration ────────────────────────────────────────────────────────
    max_duration_min: int
    friendly_count: int
    threat_count: int
    terrain_type: str
    initial_weather: str

    # ── Timeline (from EventLog) ──────────────────────────────────────────────
    events: list[dict[str, Any]] = field(default_factory=list)

    # ── Agent decisions ───────────────────────────────────────────────────────
    agent_decisions: list[dict[str, Any]] = field(default_factory=list)

    # ── Snapshots (per tick) ─────────────────────────────────────────────────
    weather_timeline: list[str] = field(default_factory=list)
    objective_timeline: list[dict[str, Any]] = field(default_factory=list)
    logistics_timeline: list[dict[str, Any]] = field(default_factory=list)

    # ── Outcome ───────────────────────────────────────────────────────────────
    success: bool = False
    termination_reason: str = ""
    duration_min: float = 0.0
    friendly_casualties: int = 0
    civilian_casualties: int = 0
    fuel_consumed: float = 0.0
    ammo_consumed: float = 0.0
    comms_failures: int = 0
    constraint_violations: list[str] = field(default_factory=list)
    roe_violations: int = 0
    objectives_completed: int = 0
    objectives_total: int = 0
    failure_modes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Full serialization for file storage and training pipeline ingestion."""
        return asdict(self)


class SimulationLogger:
    """
    Append-only builder that assembles the SimulationLog during a run.

    The engine calls log_* methods as events occur; at run end it calls
    finalise() to produce an immutable SimulationLog.
    """

    def __init__(
        self,
        mission_id: str,
        coa_id: str,
        run_seed: int,
        max_duration_min: int,
        friendly_count: int,
        threat_count: int,
        terrain_type: str = "UNKNOWN",
        initial_weather: str = "CLEAR",
    ) -> None:
        self._log = SimulationLog(
            mission_id=mission_id,
            coa_id=coa_id,
            run_seed=run_seed,
            max_duration_min=max_duration_min,
            friendly_count=friendly_count,
            threat_count=threat_count,
            terrain_type=terrain_type,
            initial_weather=initial_weather,
        )

    # ── Append methods ────────────────────────────────────────────────────────
    def log_event(self, event_dict: dict[str, Any]) -> None:
        """Append a raw event dict from the EventDispatcher log."""
        self._log.events.append(event_dict)

    def log_agent_decision(self, record: AgentDecisionRecord) -> None:
        """Record a single agent decision step."""
        self._log.agent_decisions.append(asdict(record))

    def log_weather_tick(self, weather_state: str) -> None:
        """Append current weather state to the timeline."""
        self._log.weather_timeline.append(weather_state)

    def log_objective(self, time_min: float, objective_id: str, status: str) -> None:
        self._log.objective_timeline.append(
            {"time_min": round(time_min, 2), "objective_id": objective_id, "status": status}
        )

    def log_logistics_tick(
        self,
        time_min: float,
        agent_id: str,
        fuel: float,
        ammo: float,
    ) -> None:
        self._log.logistics_timeline.append(
            {"time_min": round(time_min, 2), "agent_id": agent_id, "fuel": round(fuel, 4), "ammo": round(ammo, 4)}
        )

    # ── Finalisation ─────────────────────────────────────────────────────────
    def finalise(
        self,
        *,
        success: bool,
        termination_reason: str,
        duration_min: float,
        friendly_casualties: int,
        civilian_casualties: int,
        fuel_consumed: float,
        ammo_consumed: float,
        comms_failures: int,
        constraint_violations: list[str],
        roe_violations: int,
        objectives_completed: int,
        objectives_total: int,
        failure_modes: list[str],
    ) -> SimulationLog:
        """Seal the log and return the immutable record."""
        self._log.success = success
        self._log.termination_reason = termination_reason
        self._log.duration_min = round(duration_min, 2)
        self._log.friendly_casualties = friendly_casualties
        self._log.civilian_casualties = civilian_casualties
        self._log.fuel_consumed = round(fuel_consumed, 4)
        self._log.ammo_consumed = round(ammo_consumed, 4)
        self._log.comms_failures = comms_failures
        self._log.constraint_violations = list(dict.fromkeys(constraint_violations))
        self._log.roe_violations = roe_violations
        self._log.objectives_completed = objectives_completed
        self._log.objectives_total = objectives_total
        self._log.failure_modes = list(dict.fromkeys(failure_modes))
        return self._log
