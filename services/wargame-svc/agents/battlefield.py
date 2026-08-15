"""
Battlefield agents — Mesa-compatible entity lifecycle for the BATMAN simulation.

All agents inherit from BattlefieldAgent (which extends mesa.Agent).
Agents do NOT mutate WorldState directly; they emit SimulationEvent objects
and yield SimPy timeouts. The EventDispatcher handles state mutation.

Agent hierarchy
───────────────
BattlefieldAgent (base)
  ├── FriendlyAgent   — executes HTN tasks, moves, communicates
  ├── ThreatAgent     — uses a ThreatBehaviourPolicy
  ├── CivilianAgent   — passive; affected by engagement events
  ├── EnvironmentAgent — advances stochastic weather
  └── JudgeAgent      — read-only observer; never mutates state
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

try:
    from mesa import Agent as MesaAgent
    import mesa as _mesa_pkg
    _MESA_VERSION = tuple(int(x) for x in _mesa_pkg.__version__.split(".")[:2])
    _MESA_3 = _MESA_VERSION >= (3, 0)
except ImportError:                         # pragma: no cover
    _MESA_3 = False

    class MesaAgent:                        # type: ignore[no-redef]
        def __init__(self, unique_id: str, model: object | None = None) -> None:
            self.unique_id, self.model = unique_id, model

from agents.behaviours import ThreatBehaviourPolicy, ThreatBehaviourSelector, ThreatDecision
from simulation.events import (
    CommunicationEvent,
    DetectionEvent,
    EngagementEvent,
    FuelEvent,
    MovementEvent,
    ObjectiveEvent,
    SimulationEvent,
    WeatherEvent,
)


# ── Agent state ───────────────────────────────────────────────────────────────
@dataclass
class AgentState:
    """Canonical mutable agent state. Owned exclusively by the simulation engine."""

    agent_id: str = ""
    position: tuple[int, int] = (0, 0)
    status: str = "ACTIVE"             # ACTIVE | CASUALTY | EVACUATED | COMPLETE
    health: float = 1.0
    resources: dict[str, float] = field(default_factory=lambda: {"fuel": 1.0, "ammo": 1.0})
    visibility: float = 1.0
    decision_state: str = "IDLE"
    entity_type: str = "DEFAULT"       # INFANTRY | WHEELED | TRACKED | AVIATION



class _DummyModel:
    """Minimal Mesa-compatible model stub for offline or test use (Mesa 3.x compatible)."""
    def __init__(self) -> None:
        self._agents: list = []
        self._current_id = 0

    def next_id(self) -> int:
        self._current_id += 1
        return self._current_id

    def register_agent(self, agent: Any) -> None:
        self._agents.append(agent)

    def deregister_agent(self, agent: Any) -> None:
        if agent in self._agents:
            self._agents.remove(agent)


# ── Base agent ────────────────────────────────────────────────────────────────
class BattlefieldAgent(MesaAgent):
    """
    All battlefield entities share this interface.

    Concrete subclasses implement `decide()` which returns a list of
    SimulationEvents. The SimPy engine collects those events and passes
    them to the EventDispatcher. Agents never touch WorldState directly.
    """

    def __init__(
        self,
        unique_id: str,
        model: object | None = None,
        state: AgentState | None = None,
    ) -> None:
        if _MESA_3:
            # Mesa 3.x: Agent(model) — unique_id is auto-assigned as an int.
            # We pass a minimal fallback model if None, since Mesa 3 requires it.
            super().__init__(model or _DummyModel())
            # Override the auto-assigned unique_id with our string identifier.
            self.unique_id = unique_id  # type: ignore[assignment]
        else:
            super().__init__(unique_id, model)  # type: ignore[call-arg]
        self.state = state or AgentState(agent_id=unique_id)
        self.pos: tuple[float, float] = (0.0, 0.0)   # Mesa space position

    @property
    def position(self) -> tuple[int, int]:
        return self.state.position

    def is_active(self) -> bool:
        return self.state.status == "ACTIVE"

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list["BattlefieldAgent"],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        """
        Return a list of events for this tick. Override in subclasses.
        Agents MUST NOT mutate world_state or other agents' states here.
        """
        return []

    # ── Mesa lifecycle (called by Mesa scheduler) ─────────────────────────────
    def step(self) -> None:     # type: ignore[override]
        """Mesa step hook — not used for timing; SimPy drives the clock."""
        pass


# ── Friendly agent ────────────────────────────────────────────────────────────
class FriendlyAgent(BattlefieldAgent):
    """
    Executes the COA task queue and physically moves across the terrain.

    Task queue entries:
      {"name": str, "remaining_min": float, "target_pos": tuple[int,int]}

    Movement is waypoint-driven; each waypoint segment generates a
    MovementEvent + FuelEvent pair. Tasks are completed when all waypoints
    for that task have been traversed.
    """

    def __init__(
        self,
        unique_id: str,
        model: object | None = None,
        state: AgentState | None = None,
    ) -> None:
        super().__init__(unique_id, model, state)
        self.assigned_tasks: list[dict[str, Any]] = []
        self._waypoints: list[tuple[int, int]] = []
        self._current_task: dict[str, Any] | None = None

    def assign_task(
        self,
        name: str,
        duration_min: float,
        target_pos: tuple[int, int] | None = None,
    ) -> None:
        """Queue one task. target_pos drives spatial movement if provided."""
        self.assigned_tasks.append(
            {"name": name, "remaining_min": duration_min, "target_pos": target_pos}
        )

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list[BattlefieldAgent],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        if not self.is_active() or not self.assigned_tasks:
            return []

        # ── 1. Delta T Calculation (Single Source of Time) ───────────────────
        if getattr(self, "_last_decide_time", None) is None:
            self._last_decide_time = time_min
            return []  # First activation initializes timestamp
        
        delta_t = time_min - getattr(self, "_last_decide_time")
        self._last_decide_time = time_min
        
        if delta_t <= 0:
            return []

        events: list[SimulationEvent] = []
        task = self.assigned_tasks[0]
        weather_effects = getattr(world_state, "weather_effects", None)
        weather_factor = getattr(weather_effects, "movement_speed", 1.0) if weather_effects else 1.0
        weather_comms  = getattr(weather_effects, "communication_quality", 1.0) if weather_effects else 1.0

        # ── Movement ─────────────────────────────────────────────────────────
        target_pos = task.get("target_pos")
        if target_pos and self.state.position != target_pos:
            origin = self.state.position
            
            # Physics: base speed 30 km/h.
            base_speed_kmh = 30.0
            effective_speed_kmh = base_speed_kmh * weather_factor
            speed_km_per_min = effective_speed_kmh / 60.0
            
            # Distance moved during this tick
            distance_km = speed_km_per_min * delta_t
            
            import math
            dist_to_target = math.hypot(target_pos[0] - origin[0], target_pos[1] - origin[1])
            actual_distance_km = min(distance_km, dist_to_target)
            
            if dist_to_target > 0:
                step_x = (target_pos[0] - origin[0]) / dist_to_target * actual_distance_km
                step_y = (target_pos[1] - origin[1]) / dist_to_target * actual_distance_km
                dest = (origin[0] + step_x, origin[1] + step_y)
            else:
                dest = origin
            
            fuel_rate = 0.008       # fraction of tank per km
            fuel_consumed = fuel_rate * actual_distance_km
            fuel_before = self.state.resources.get("fuel", 1.0)
            fuel_after = max(0.0, fuel_before - fuel_consumed)
            reserve_breach = fuel_after < 0.20

            corr = str(rng.randint(10000, 99999))
            events.append(MovementEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                origin=origin,
                destination=dest,
                distance_km=round(actual_distance_km, 3),
                travel_time_min=round(delta_t, 3),
                speed_kmh=round(effective_speed_kmh, 2),
                terrain_type="UNKNOWN",
                road_used=False,
                waypoints_remaining=round(max(0.0, dist_to_target - actual_distance_km), 3),
                correlation_id=corr,
            ))
            events.append(FuelEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                fuel_consumed=round(fuel_consumed, 5),
                fuel_remaining=round(fuel_after, 5),
                reserve_breach=reserve_breach,
                movement_distance_km=round(actual_distance_km, 3),
                correlation_id=corr,
            ))
            task["remaining_min"] -= (delta_t * weather_factor)

        else:
            # No spatial movement — pure task time consumption.
            task["remaining_min"] -= (delta_t * weather_factor)

        # ── Periodic SITREP comms ─────────────────────────────────────────────
        if rng.random() < 0.25:
            delivered, quality = rng.random() < weather_comms, weather_comms * rng.uniform(0.7, 1.0)
            events.append(CommunicationEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                recipient_id="HQ",
                delivered=delivered,
                link_quality=round(quality, 4),
                message_type="SITREP",
                ew_interference=getattr(world_state, "ew_level", 0.0),
            ))

        # ── Task completion ───────────────────────────────────────────────────
        if task["remaining_min"] <= 0:
            self.assigned_tasks.pop(0)
            self.state.decision_state = "AWAITING_TASK" if self.assigned_tasks else "COMPLETE"
            events.append(ObjectiveEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                objective_id=task["name"],
                objective_status="ACHIEVED",
                description=f"Task '{task['name']}' completed by {self.unique_id}",
            ))
        else:
            self.state.decision_state = "EXECUTING_TASK"

        return events


# ── Threat agent ──────────────────────────────────────────────────────────────
class ThreatAgent(BattlefieldAgent):
    """
    Uses an injected ThreatBehaviourPolicy to decide actions.

    The behaviour is selected at construction time by ThreatBehaviourSelector
    and can change at runtime if health drops below the retreat threshold.
    """

    def __init__(
        self,
        unique_id: str,
        model: object | None = None,
        state: AgentState | None = None,
        behaviour: ThreatBehaviourPolicy | None = None,
        threat_probability: float = 0.3,
    ) -> None:
        super().__init__(unique_id, model, state)
        self._behaviour = behaviour or PatrolBehaviourDefault()
        self._threat_probability = threat_probability

    # allow runtime behaviour replacement (e.g., switch to Retreat on damage)
    def set_behaviour(self, behaviour: ThreatBehaviourPolicy) -> None:
        self._behaviour = behaviour

    @property
    def behaviour_name(self) -> str:
        return self._behaviour.name

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list[BattlefieldAgent],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        if not self.is_active():
            return []

        # Dynamic behaviour switch on low health.
        if self.state.health < 0.4 and self._behaviour.name != "RETREAT":
            from agents.behaviours import RetreatBehaviour
            self.set_behaviour(RetreatBehaviour())

        visible_states = [e.state for e in visible_entities if e.unique_id != self.unique_id]
        decision: ThreatDecision = self._behaviour.decide_action(
            agent_state=self.state,
            world_state=world_state,
            visible_entities=visible_states,
            rng=rng,
        )
        self.state.decision_state = decision.action

        events: list[SimulationEvent] = []
        weather_effects = getattr(world_state, "weather_effects", None)
        detection_factor = getattr(weather_effects, "detection_probability", 1.0) if weather_effects else 1.0

        if decision.action == "ENGAGE" and decision.target_id:
            hit_prob = min(0.8, self._threat_probability * detection_factor * self.state.health)
            result_casualty = rng.random() < hit_prob * 0.25   # lethal outcome is a subset
            ammo = self.state.resources.get("ammo", 1.0)
            events.append(EngagementEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                target_id=decision.target_id,
                hit_probability=round(hit_prob, 4),
                result_casualty=result_casualty,
                weapon_type="SMALL_ARMS",
                ammo_consumed=0.05,
                suppression=rng.random() < hit_prob * 0.6,
                roe_compliant=True,
            ))

        elif decision.action == "MOVE" and decision.target_position:
            origin = self.state.position
            dest = decision.target_position
            corr = str(rng.randint(10000, 99999))
            events.append(MovementEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                origin=origin,
                destination=dest,
                distance_km=1.0,
                travel_time_min=5.0,
                speed_kmh=15.0,
                terrain_type="UNKNOWN",
                correlation_id=corr,
            ))

        return events


# Simple default that avoids circular import before behaviours module loads.
class PatrolBehaviourDefault:
    """Minimal patrol stand-in for agents initialised before behaviours are injected."""
    name = "PATROL"

    def decide_action(self, agent_state: Any, world_state: Any, visible_entities: list[Any], rng: random.Random) -> ThreatDecision:
        return ThreatDecision(action="HOLD", priority=0.2, rationale="Default hold")


# ── Civilian agent ────────────────────────────────────────────────────────────
class CivilianAgent(BattlefieldAgent):
    """
    Represents non-combatant population.

    Civilians move randomly when under threat; their density and movement
    affect engagement outcomes and ROE compliance checks.
    """

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list[BattlefieldAgent],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        if not self.is_active():
            return []

        # Check if any engagements are nearby.
        threat_nearby = any(
            isinstance(e, ThreatAgent) and e.is_active() and
            abs(e.position[0] - self.position[0]) + abs(e.position[1] - self.position[1]) <= 2
            for e in visible_entities
        )
        if threat_nearby:
            self.state.decision_state = "FLEEING"
            pos = self.state.position
            dx, dy = rng.choice([-1, 0, 1]), rng.choice([-1, 0, 1])
            dest = (max(0, pos[0] + dx), max(0, pos[1] + dy))
            return [MovementEvent.create(
                time_min=time_min,
                agent_id=self.unique_id,
                origin=pos,
                destination=dest,
                distance_km=1.0,
                travel_time_min=10.0,
                speed_kmh=6.0,
                terrain_type="URBAN",
            )]
        self.state.decision_state = "SHELTERING"
        return []


# ── Environment agent ─────────────────────────────────────────────────────────
class EnvironmentAgent(BattlefieldAgent):
    """Advances the stochastic weather model and emits WeatherEvents on transitions."""

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list[BattlefieldAgent],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        weather_model = getattr(world_state, "weather_model", None)
        if weather_model is None:
            return []
        previous = weather_model.state.value
        current_state = weather_model.advance()
        current_val = current_state.value
        self.state.decision_state = "UPDATING_WEATHER"

        if current_val != previous:
            effects = weather_model.current_effects
            return [WeatherEvent.create(
                time_min=time_min,
                from_state=previous,
                to_state=current_val,
                visibility_factor=effects.visibility,
                movement_factor=effects.movement_speed,
                comms_factor=effects.communication_quality,
                sensor_factor=effects.sensor_effectiveness,
            )]
        return []


# ── Judge agent ───────────────────────────────────────────────────────────────
class JudgeAgent(BattlefieldAgent):
    """
    Read-only evaluator. Appends observations; NEVER mutates simulation state.

    Evaluates: objective completion, ROE compliance, civilian safety,
    force effectiveness, and constraint violations.
    """

    def __init__(
        self,
        unique_id: str = "judge",
        model: object | None = None,
    ) -> None:
        super().__init__(unique_id, model)
        self.observations: list[dict[str, Any]] = []

    def evaluate(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        """Pure evaluation — returns a verdict dict without mutating anything."""
        objectives_done = snapshot.get("objectives_completed", 0)
        objectives_total = max(snapshot.get("objectives_total", 1), 1)
        objectives_complete = objectives_done >= objectives_total

        violations = list(snapshot.get("constraint_violations", ()))
        roe_events = snapshot.get("roe_events", 0)
        if snapshot.get("civilian_casualties", 0) > 0:
            violations.append("CIVILIAN_SAFETY")
        if roe_events > 0:
            violations.append("ROE_VIOLATION")

        friendly_casualties = snapshot.get("friendly_casualties", 0)
        friendly_count = max(snapshot.get("friendly_count", 1), 1)
        force_effective = friendly_casualties < friendly_count

        return {
            "objectives_complete": objectives_complete,
            "objectives_done": objectives_done,
            "objectives_total": objectives_total,
            "valid": not violations,
            "violations": tuple(dict.fromkeys(violations)),
            "roe_violations": roe_events,
            "friendly_force_effective": force_effective,
            "friendly_casualties": friendly_casualties,
        }

    def decide(
        self,
        time_min: float,
        world_state: Any,
        visible_entities: list[BattlefieldAgent],
        rng: random.Random,
    ) -> list[SimulationEvent]:
        """Observe only — returns no events and mutates nothing."""
        snapshot = getattr(world_state, "snapshot", {})
        verdict = self.evaluate(snapshot)
        self.observations.append({
            "time_min": time_min,
            **snapshot,
            "evaluation": verdict,
        })
        return []
