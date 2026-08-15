"""
Immutable, versioned simulation event taxonomy for the BATMAN DES engine.

All events are frozen dataclasses — they can be replayed, logged, and audited
without any risk of post-hoc mutation. Every event carries an event_id (UUID),
a correlation_id (to link related cascading events), and a schema version tag
so that future schema changes remain backward-compatible.

Event hierarchy
───────────────
SimulationEvent  (base)
  ├── MovementEvent
  ├── FuelEvent
  ├── DetectionEvent
  ├── EngagementEvent
  ├── CommunicationEvent
  ├── LogisticsEvent
  ├── ObjectiveEvent
  ├── WeatherEvent
  └── MissionEndEvent
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Schema version ────────────────────────────────────────────────────────────
EVENT_SCHEMA_VERSION = "2.0.0"


# ── Event type vocabulary ─────────────────────────────────────────────────────
class SimulationEventType(str, Enum):
    """Canonical set of events understood by the dispatcher."""

    MOVEMENT = "MOVEMENT"
    FUEL = "FUEL"
    DETECTION = "DETECTION"
    ENGAGEMENT = "ENGAGEMENT"
    COMMUNICATION = "COMMUNICATION"
    LOGISTICS = "LOGISTICS"
    OBJECTIVE = "OBJECTIVE"
    WEATHER = "WEATHER"
    MISSION_END = "MISSION_END"


# ── Base event ────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class SimulationEvent:
    """
    Root simulation event.

    Python 3.10 dataclass inheritance rule: fields with defaults in the parent
    class mean all child-class fields must also have defaults. We therefore give
    all base fields sentinel defaults and enforce correct values via @classmethod
    factories on the concrete subclasses.
    """

    event_type: SimulationEventType = SimulationEventType.WEATHER
    time_min: float = 0.0
    agent_id: str = ""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = ""
    version: str = EVENT_SCHEMA_VERSION

    def to_log_dict(self) -> dict[str, Any]:
        """Serialise the base fields for the structured event log."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "time_min": round(self.time_min, 4),
            "agent_id": self.agent_id,
            "correlation_id": self.correlation_id,
            "version": self.version,
        }


# ── Concrete events ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MovementEvent(SimulationEvent):
    """Emitted when an agent successfully traverses one waypoint segment."""

    event_type: SimulationEventType = SimulationEventType.MOVEMENT
    origin: tuple[int, int] = (0, 0)
    destination: tuple[int, int] = (0, 0)
    distance_km: float = 0.0
    travel_time_min: float = 0.0
    speed_kmh: float = 0.0
    terrain_type: str = "UNKNOWN"
    road_used: bool = False
    waypoints_remaining: int = 0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "origin": self.origin,
            "destination": self.destination,
            "distance_km": round(self.distance_km, 3),
            "travel_time_min": round(self.travel_time_min, 3),
            "speed_kmh": round(self.speed_kmh, 2),
            "terrain_type": self.terrain_type,
            "road_used": self.road_used,
            "waypoints_remaining": self.waypoints_remaining,
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        origin: tuple[int, int],
        destination: tuple[int, int],
        distance_km: float,
        travel_time_min: float,
        speed_kmh: float,
        terrain_type: str = "UNKNOWN",
        road_used: bool = False,
        waypoints_remaining: int = 0,
        correlation_id: str = "",
    ) -> "MovementEvent":
        return cls(
            event_type=SimulationEventType.MOVEMENT,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            travel_time_min=travel_time_min,
            speed_kmh=speed_kmh,
            terrain_type=terrain_type,
            road_used=road_used,
            waypoints_remaining=waypoints_remaining,
        )


@dataclass(frozen=True)
class FuelEvent(SimulationEvent):
    """Emitted when an agent consumes fuel (always paired with MovementEvent)."""

    event_type: SimulationEventType = SimulationEventType.FUEL
    fuel_consumed: float = 0.0
    fuel_remaining: float = 1.0
    reserve_breach: bool = False
    movement_distance_km: float = 0.0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "fuel_consumed": round(self.fuel_consumed, 4),
            "fuel_remaining": round(self.fuel_remaining, 4),
            "reserve_breach": self.reserve_breach,
            "movement_distance_km": round(self.movement_distance_km, 3),
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        fuel_consumed: float,
        fuel_remaining: float,
        reserve_breach: bool = False,
        movement_distance_km: float = 0.0,
        correlation_id: str = "",
    ) -> "FuelEvent":
        return cls(
            event_type=SimulationEventType.FUEL,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            fuel_consumed=fuel_consumed,
            fuel_remaining=fuel_remaining,
            reserve_breach=reserve_breach,
            movement_distance_km=movement_distance_km,
        )


@dataclass(frozen=True)
class DetectionEvent(SimulationEvent):
    """Emitted by the sensor handler when a detection attempt is resolved."""

    event_type: SimulationEventType = SimulationEventType.DETECTION
    target_id: str = ""
    detected: bool = False
    detection_probability: float = 0.0
    detection_range_km: float = 0.0
    weather_factor: float = 1.0
    terrain_cover_factor: float = 1.0
    ew_degradation: float = 0.0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "target_id": self.target_id,
            "detected": self.detected,
            "detection_probability": round(self.detection_probability, 4),
            "detection_range_km": round(self.detection_range_km, 3),
            "weather_factor": round(self.weather_factor, 3),
            "terrain_cover_factor": round(self.terrain_cover_factor, 3),
            "ew_degradation": round(self.ew_degradation, 3),
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        target_id: str,
        detected: bool,
        detection_probability: float,
        detection_range_km: float = 0.0,
        weather_factor: float = 1.0,
        terrain_cover_factor: float = 1.0,
        ew_degradation: float = 0.0,
        correlation_id: str = "",
    ) -> "DetectionEvent":
        return cls(
            event_type=SimulationEventType.DETECTION,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            target_id=target_id,
            detected=detected,
            detection_probability=detection_probability,
            detection_range_km=detection_range_km,
            weather_factor=weather_factor,
            terrain_cover_factor=terrain_cover_factor,
            ew_degradation=ew_degradation,
        )


@dataclass(frozen=True)
class EngagementEvent(SimulationEvent):
    """Emitted when an agent fires on a target; result records the casualty outcome."""

    event_type: SimulationEventType = SimulationEventType.ENGAGEMENT
    target_id: str = ""
    weapon_type: str = "SMALL_ARMS"
    hit_probability: float = 0.0
    result_casualty: bool = False
    ammo_consumed: float = 0.05
    suppression: bool = False
    roe_compliant: bool = True

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "target_id": self.target_id,
            "weapon_type": self.weapon_type,
            "hit_probability": round(self.hit_probability, 4),
            "result_casualty": self.result_casualty,
            "ammo_consumed": round(self.ammo_consumed, 4),
            "suppression": self.suppression,
            "roe_compliant": self.roe_compliant,
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        target_id: str,
        hit_probability: float,
        result_casualty: bool,
        weapon_type: str = "SMALL_ARMS",
        ammo_consumed: float = 0.05,
        suppression: bool = False,
        roe_compliant: bool = True,
        correlation_id: str = "",
    ) -> "EngagementEvent":
        return cls(
            event_type=SimulationEventType.ENGAGEMENT,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            target_id=target_id,
            weapon_type=weapon_type,
            hit_probability=hit_probability,
            result_casualty=result_casualty,
            ammo_consumed=ammo_consumed,
            suppression=suppression,
            roe_compliant=roe_compliant,
        )


@dataclass(frozen=True)
class CommunicationEvent(SimulationEvent):
    """Emitted when a comms transmission is resolved by the communication handler."""

    event_type: SimulationEventType = SimulationEventType.COMMUNICATION
    recipient_id: str = ""
    message_type: str = "SITREP"
    delivered: bool = True
    link_quality: float = 1.0
    ew_interference: float = 0.0
    distance_km: float = 0.0
    terrain_obstruction: float = 0.0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "delivered": self.delivered,
            "link_quality": round(self.link_quality, 4),
            "ew_interference": round(self.ew_interference, 3),
            "distance_km": round(self.distance_km, 3),
            "terrain_obstruction": round(self.terrain_obstruction, 3),
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        recipient_id: str,
        delivered: bool,
        link_quality: float,
        message_type: str = "SITREP",
        ew_interference: float = 0.0,
        distance_km: float = 0.0,
        terrain_obstruction: float = 0.0,
        correlation_id: str = "",
    ) -> "CommunicationEvent":
        return cls(
            event_type=SimulationEventType.COMMUNICATION,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            recipient_id=recipient_id,
            message_type=message_type,
            delivered=delivered,
            link_quality=link_quality,
            ew_interference=ew_interference,
            distance_km=distance_km,
            terrain_obstruction=terrain_obstruction,
        )


@dataclass(frozen=True)
class LogisticsEvent(SimulationEvent):
    """Emitted on any resupply or resource violation check."""

    event_type: SimulationEventType = SimulationEventType.LOGISTICS
    resource_type: str = "FUEL"
    amount_consumed: float = 0.0
    amount_remaining: float = 1.0
    resupply: bool = False
    violation: str = ""

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "resource_type": self.resource_type,
            "amount_consumed": round(self.amount_consumed, 4),
            "amount_remaining": round(self.amount_remaining, 4),
            "resupply": self.resupply,
            "violation": self.violation,
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        resource_type: str,
        amount_consumed: float,
        amount_remaining: float,
        resupply: bool = False,
        violation: str = "",
        correlation_id: str = "",
    ) -> "LogisticsEvent":
        return cls(
            event_type=SimulationEventType.LOGISTICS,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            resource_type=resource_type,
            amount_consumed=amount_consumed,
            amount_remaining=amount_remaining,
            resupply=resupply,
            violation=violation,
        )


@dataclass(frozen=True)
class ObjectiveEvent(SimulationEvent):
    """Emitted when an objective state changes."""

    event_type: SimulationEventType = SimulationEventType.OBJECTIVE
    objective_id: str = ""
    objective_status: str = "ACHIEVED"   # ACHIEVED | FAILED | UPDATED
    description: str = ""

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "objective_id": self.objective_id,
            "objective_status": self.objective_status,
            "description": self.description,
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str,
        objective_id: str,
        objective_status: str,
        description: str = "",
        correlation_id: str = "",
    ) -> "ObjectiveEvent":
        return cls(
            event_type=SimulationEventType.OBJECTIVE,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            objective_id=objective_id,
            objective_status=objective_status,
            description=description,
        )


@dataclass(frozen=True)
class WeatherEvent(SimulationEvent):
    """Emitted when the stochastic weather model transitions state."""

    event_type: SimulationEventType = SimulationEventType.WEATHER
    from_state: str = "CLEAR"
    to_state: str = "CLEAR"
    visibility_factor: float = 1.0
    movement_factor: float = 1.0
    comms_factor: float = 1.0
    sensor_factor: float = 1.0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "from_state": self.from_state,
            "to_state": self.to_state,
            "visibility_factor": round(self.visibility_factor, 3),
            "movement_factor": round(self.movement_factor, 3),
            "comms_factor": round(self.comms_factor, 3),
            "sensor_factor": round(self.sensor_factor, 3),
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        agent_id: str = "environment",
        from_state: str,
        to_state: str,
        visibility_factor: float = 1.0,
        movement_factor: float = 1.0,
        comms_factor: float = 1.0,
        sensor_factor: float = 1.0,
        correlation_id: str = "",
    ) -> "WeatherEvent":
        return cls(
            event_type=SimulationEventType.WEATHER,
            time_min=time_min,
            agent_id=agent_id,
            correlation_id=correlation_id,
            from_state=from_state,
            to_state=to_state,
            visibility_factor=visibility_factor,
            movement_factor=movement_factor,
            comms_factor=comms_factor,
            sensor_factor=sensor_factor,
        )


@dataclass(frozen=True)
class MissionEndEvent(SimulationEvent):
    """Final event emitted once per simulation run; signals all processes to halt."""

    event_type: SimulationEventType = SimulationEventType.MISSION_END
    termination_reason: str = "OBJECTIVES_COMPLETED"
    success: bool = False
    objectives_completed: int = 0
    objectives_total: int = 0
    total_friendly_casualties: int = 0
    total_civilian_casualties: int = 0
    duration_min: float = 0.0

    def to_log_dict(self) -> dict[str, Any]:
        return {
            **super().to_log_dict(),
            "termination_reason": self.termination_reason,
            "success": self.success,
            "objectives_completed": self.objectives_completed,
            "objectives_total": self.objectives_total,
            "total_friendly_casualties": self.total_friendly_casualties,
            "total_civilian_casualties": self.total_civilian_casualties,
            "duration_min": round(self.duration_min, 2),
        }

    @classmethod
    def create(
        cls,
        *,
        time_min: float,
        termination_reason: str,
        success: bool,
        objectives_completed: int,
        objectives_total: int,
        total_friendly_casualties: int = 0,
        total_civilian_casualties: int = 0,
        correlation_id: str = "",
    ) -> "MissionEndEvent":
        return cls(
            event_type=SimulationEventType.MISSION_END,
            time_min=time_min,
            agent_id="dispatcher",
            correlation_id=correlation_id,
            termination_reason=termination_reason,
            success=success,
            objectives_completed=objectives_completed,
            objectives_total=objectives_total,
            total_friendly_casualties=total_friendly_casualties,
            total_civilian_casualties=total_civilian_casualties,
            duration_min=time_min,
        )
