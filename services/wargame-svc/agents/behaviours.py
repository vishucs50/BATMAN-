"""
Threat Behaviour Framework — Strategy Pattern implementations.

ThreatAgent selects a ThreatBehaviourPolicy at initialisation based on the
injected ThreatAssessment. Behaviours are independently testable, stateless
strategy objects. New behaviour types can be added without modifying ThreatAgent.

Hierarchy
─────────
ThreatBehaviourPolicy (Protocol / ABC)
  ├── PatrolBehaviour
  ├── ReconBehaviour
  ├── AmbushBehaviour
  ├── DefensiveBehaviour
  ├── RetreatBehaviour
  └── InfiltrationBehaviour

Selection
─────────
ThreatBehaviourSelector.select(threat_assessment, mission_type, terrain_type)
  → ThreatBehaviourPolicy
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


# ── Decision output ───────────────────────────────────────────────────────────
@dataclass(frozen=True)
class ThreatDecision:
    """The output of a behaviour's decide_action call."""

    action: str                       # MOVE | ENGAGE | OBSERVE | RETREAT | HOLD
    target_id: str = ""               # relevant for ENGAGE
    target_position: tuple[int, int] | None = None
    priority: float = 0.5             # 0.0 = low, 1.0 = high
    rationale: str = ""


# ── Protocol ──────────────────────────────────────────────────────────────────
@runtime_checkable
class ThreatBehaviourPolicy(Protocol):
    """
    Contract for all threat behaviour implementations.

    Implementors MUST NOT mutate AgentState or WorldState directly.
    They return a ThreatDecision which the ThreatAgent uses to emit events.
    """

    @property
    def name(self) -> str:
        """Human-readable behaviour name (used in logs and explanations)."""
        ...

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        """
        Produce the next action given the observable battlefield state.

        Parameters
        ----------
        agent_state:      Current AgentState of this threat agent.
        world_state:      Read-only WorldState snapshot.
        visible_entities: List of AgentState objects within sensor range.
        rng:              Seeded random generator — ensures reproducibility.
        """
        ...


# ── Patrol ────────────────────────────────────────────────────────────────────
class PatrolBehaviour:
    """
    Moves the agent along a looping patrol route.

    Fires on enemies of opportunity when within weapon range (< 0.8 km proxy).
    Used when the threat assessment indicates a persistent area-denial posture.
    """

    name = "PATROL"

    def __init__(self, waypoints: list[tuple[int, int]] | None = None) -> None:
        self._waypoints = waypoints or [(1, 0), (2, 1), (1, 2), (0, 1)]
        self._index = 0

    @property
    def current_waypoint(self) -> tuple[int, int]:
        return self._waypoints[self._index % len(self._waypoints)]

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        friendlies = [e for e in visible_entities if getattr(e, "status", "") == "ACTIVE"]
        if friendlies and rng.random() < 0.3:
            target = rng.choice(friendlies)
            return ThreatDecision(
                action="ENGAGE",
                target_id=getattr(target, "agent_id", "unknown"),
                target_position=getattr(target, "position", None),
                priority=0.7,
                rationale="Opportunity fire during patrol",
            )
        next_wp = self.current_waypoint
        self._index += 1
        return ThreatDecision(
            action="MOVE",
            target_position=next_wp,
            priority=0.4,
            rationale=f"Patrolling waypoint {next_wp}",
        )


# ── Recon ─────────────────────────────────────────────────────────────────────
class ReconBehaviour:
    """
    Moves toward friendly forces while maintaining detection range margin.

    Does not engage; purpose is intelligence gathering. High mobility.
    """

    name = "RECON"
    _SAFE_DISTANCE_CELLS = 3   # stays this many cells from friendlies

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        friendlies = [e for e in visible_entities if getattr(e, "status", "") == "ACTIVE"]
        if not friendlies:
            # Advance toward objective centre
            dx = rng.choice([-1, 0, 1])
            dy = rng.choice([-1, 0, 1])
            pos = agent_state.position
            return ThreatDecision(
                action="MOVE",
                target_position=(pos[0] + dx, pos[1] + dy),
                priority=0.5,
                rationale="Advancing toward area of interest",
            )

        # If too close, fall back.
        closest = min(
            friendlies,
            key=lambda e: abs(e.position[0] - agent_state.position[0])
                         + abs(e.position[1] - agent_state.position[1]),
        )
        dist = (
            abs(closest.position[0] - agent_state.position[0])
            + abs(closest.position[1] - agent_state.position[1])
        )
        if dist < self._SAFE_DISTANCE_CELLS:
            # Retreat away
            dx = agent_state.position[0] - closest.position[0]
            dy = agent_state.position[1] - closest.position[1]
            pos = agent_state.position
            return ThreatDecision(
                action="MOVE",
                target_position=(pos[0] + (1 if dx >= 0 else -1), pos[1] + (1 if dy >= 0 else -1)),
                priority=0.6,
                rationale="Maintaining safe observation distance",
            )

        return ThreatDecision(
            action="OBSERVE",
            priority=0.5,
            rationale="Observing friendly forces from safe distance",
        )


# ── Ambush ────────────────────────────────────────────────────────────────────
class AmbushBehaviour:
    """
    Holds position in high-cover terrain and fires on approaching friendlies.

    Maximum lethality posture; used for high-probability threat assessments
    or when the terrain terrain_cover > 0.5.
    """

    name = "AMBUSH"
    _TRIGGER_DISTANCE_CELLS = 2

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        friendlies = [e for e in visible_entities if getattr(e, "status", "") == "ACTIVE"]
        within_range = [
            f for f in friendlies
            if (abs(f.position[0] - agent_state.position[0])
                + abs(f.position[1] - agent_state.position[1])) <= self._TRIGGER_DISTANCE_CELLS
        ]
        if within_range:
            target = rng.choice(within_range)
            return ThreatDecision(
                action="ENGAGE",
                target_id=getattr(target, "agent_id", "unknown"),
                target_position=target.position,
                priority=0.95,
                rationale="Ambush triggered on approaching friendly forces",
            )
        # Hold and wait.
        return ThreatDecision(
            action="HOLD",
            priority=0.2,
            rationale="Holding ambush position",
        )


# ── Defensive ─────────────────────────────────────────────────────────────────
class DefensiveBehaviour:
    """
    Holds an objective position and engages anything within range.

    Used when the threat is defending a key location.
    """

    name = "DEFENSIVE"

    def __init__(self, objective_pos: tuple[int, int] = (0, 0)) -> None:
        self.objective_pos = objective_pos

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        # If not at objective, move there.
        if agent_state.position != self.objective_pos:
            return ThreatDecision(
                action="MOVE",
                target_position=self.objective_pos,
                priority=0.8,
                rationale="Moving to defend objective position",
            )

        friendlies = [e for e in visible_entities if getattr(e, "status", "") == "ACTIVE"]
        if friendlies and rng.random() < 0.6:
            target = rng.choice(friendlies)
            return ThreatDecision(
                action="ENGAGE",
                target_id=getattr(target, "agent_id", "unknown"),
                target_position=getattr(target, "position", None),
                priority=0.85,
                rationale="Defending objective from advancing friendlies",
            )
        return ThreatDecision(
            action="HOLD",
            priority=0.3,
            rationale="Holding defensive position at objective",
        )


# ── Retreat ───────────────────────────────────────────────────────────────────
class RetreatBehaviour:
    """
    Moves away from all friendly forces. Used when threat health drops below 50%.

    Low engagement probability; prioritises survival.
    """

    name = "RETREAT"

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        friendlies = [e for e in visible_entities if getattr(e, "status", "") == "ACTIVE"]
        pos = agent_state.position

        if friendlies:
            avg_x = sum(f.position[0] for f in friendlies) / len(friendlies)
            avg_y = sum(f.position[1] for f in friendlies) / len(friendlies)
            dx = 1 if pos[0] >= avg_x else -1
            dy = 1 if pos[1] >= avg_y else -1
        else:
            dx, dy = rng.choice([-1, 1]), rng.choice([-1, 1])

        return ThreatDecision(
            action="MOVE",
            target_position=(pos[0] + dx, pos[1] + dy),
            priority=0.9,
            rationale="Retreating from superior friendly force",
        )


# ── Infiltration ──────────────────────────────────────────────────────────────
class InfiltrationBehaviour:
    """
    Moves covertly toward a target, avoiding detection. Attacks only when adjacent.

    Used for asymmetric/sub-conventional threat types (infiltration, sabotage).
    """

    name = "INFILTRATION"
    _TARGET_POS_DEFAULT = (2, 2)

    def __init__(self, target_pos: tuple[int, int] | None = None) -> None:
        self._target_pos = target_pos or self._TARGET_POS_DEFAULT

    def decide_action(
        self,
        agent_state: Any,
        world_state: Any,   # noqa: ARG002
        visible_entities: list[Any],
        rng: random.Random,
    ) -> ThreatDecision:
        pos = agent_state.position
        adjacent = [
            f for f in visible_entities
            if getattr(f, "status", "") == "ACTIVE"
            and abs(f.position[0] - pos[0]) + abs(f.position[1] - pos[1]) <= 1
        ]
        if adjacent:
            target = rng.choice(adjacent)
            return ThreatDecision(
                action="ENGAGE",
                target_id=getattr(target, "agent_id", "unknown"),
                target_position=target.position,
                priority=1.0,
                rationale="Close-range infiltration strike",
            )
        # Covert advance toward target.
        dx = 0 if self._target_pos[0] == pos[0] else (1 if self._target_pos[0] > pos[0] else -1)
        dy = 0 if self._target_pos[1] == pos[1] else (1 if self._target_pos[1] > pos[1] else -1)
        return ThreatDecision(
            action="MOVE",
            target_position=(pos[0] + dx, pos[1] + dy),
            priority=0.7,
            rationale="Covert infiltration advance",
        )


# ── Behaviour Selector ────────────────────────────────────────────────────────
_MISSION_TYPE_MAP: dict[str, str] = {
    "COUNTER_INFILTRATION": "AMBUSH",
    "COUNTER_TERRORISM":    "DEFENSIVE",
    "HIGH_ALTITUDE_LOGISTICS": "PATROL",
    "HADR":                 "PATROL",
}

_TERRAIN_TYPE_MAP: dict[str, str] = {
    "FOREST":       "AMBUSH",
    "URBAN":        "DEFENSIVE",
    "HIGH_ALTITUDE": "RECON",
    "RIPARIAN":     "INFILTRATION",
}


class ThreatBehaviourSelector:
    """
    Selects the most appropriate threat behaviour given available context.

    Selection priority:
      1. Threat probability >= 0.8  → AMBUSH
      2. Agent health < 0.4         → RETREAT
      3. Mission type mapping
      4. Terrain type mapping
      5. Default                    → PATROL
    """

    @staticmethod
    def select(
        *,
        threat_probability: float = 0.5,
        agent_health: float = 1.0,
        mission_type: str = "UNKNOWN",
        terrain_type: str = "UNKNOWN",
        objective_pos: tuple[int, int] | None = None,
    ) -> ThreatBehaviourPolicy:
        if agent_health < 0.4:
            return RetreatBehaviour()
        if threat_probability >= 0.80:
            return AmbushBehaviour()
        if mission_type.upper() in _MISSION_TYPE_MAP:
            chosen = _MISSION_TYPE_MAP[mission_type.upper()]
        elif terrain_type.upper() in _TERRAIN_TYPE_MAP:
            chosen = _TERRAIN_TYPE_MAP[terrain_type.upper()]
        else:
            chosen = "PATROL"

        behaviour_map: dict[str, ThreatBehaviourPolicy] = {
            "PATROL":        PatrolBehaviour(),
            "RECON":         ReconBehaviour(),
            "AMBUSH":        AmbushBehaviour(),
            "DEFENSIVE":     DefensiveBehaviour(objective_pos or (0, 0)),
            "RETREAT":       RetreatBehaviour(),
            "INFILTRATION":  InfiltrationBehaviour(objective_pos),
        }
        return behaviour_map.get(chosen, PatrolBehaviour())
