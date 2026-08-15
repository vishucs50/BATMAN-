"""
Physics Engine — owns all domain physics calculations for the BATMAN simulation.

The Physics Engine is a pure-function module (stateless class with injected
dependencies). The EventDispatcher calls the Physics Engine inside event
handlers — NOT directly. This keeps the dispatcher decoupled from physics.

Responsibilities
────────────────
• Movement speed computation (terrain + weather + load + slope + lighting)
• Fuel consumption modelling (distance × vehicle type × terrain factor)
• Line-of-sight (LOS) determination
• Visibility radius calculation
• Engagement hit probability
• Sensor detection probability (wraps sensor.model)
• Communications link quality (wraps comms.model)

Physics Engine does NOT:
  • Mutate WorldState (it returns calculated values only)
  • Schedule SimPy events
  • Access the event log
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from math import sqrt
from typing import Any

from terrain.model import TerrainEngine
from sensor.model import SensorModel
from comms.model import CommunicationModel


# ── Constants ─────────────────────────────────────────────────────────────────
# Fuel consumption in fraction-of-tank per km, indexed by vehicle category.
_FUEL_RATE_PER_KM: dict[str, float] = {
    "INFANTRY":  0.000,   # infantry does not consume vehicle fuel
    "WHEELED":   0.008,   # ~125 km on one full tank
    "TRACKED":   0.012,   # heavier consumption
    "AVIATION":  0.045,   # rotary-wing is most expensive
    "DEFAULT":   0.008,
}

# Base movement speed (km/h) by entity class.
_BASE_SPEED_KMH: dict[str, float] = {
    "INFANTRY":  5.0,
    "WHEELED":  55.0,
    "TRACKED":  40.0,
    "AVIATION": 220.0,
    "DEFAULT":  30.0,
}

# Effective engagement range (km) and base hit probability by weapon class.
_WEAPON_PARAMS: dict[str, tuple[float, float]] = {
    "SMALL_ARMS":    (0.5,  0.35),
    "LMG":           (0.8,  0.45),
    "HMG":           (1.2,  0.55),
    "MORTAR":        (5.0,  0.40),
    "ATGM":          (3.5,  0.70),
    "SHOULDER_AA":   (4.0,  0.60),
    "DEFAULT":       (0.5,  0.35),
}


# ── Movement result ───────────────────────────────────────────────────────────
@dataclass(frozen=True)
class MovementResult:
    """Output of physics.compute_movement — ready for MovementEvent construction."""

    speed_kmh: float
    travel_time_min: float
    fuel_consumed: float       # fraction of tank
    fuel_remaining: float
    reserve_breach: bool
    road_used: bool
    terrain_type: str
    impassable: bool


# ── Engagement result ─────────────────────────────────────────────────────────
@dataclass(frozen=True)
class EngagementResult:
    """Output of physics.compute_engagement."""

    hit_probability: float
    result_casualty: bool
    ammo_consumed: float
    suppression: bool
    roe_compliant: bool


# ── LOS result ────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class LOSResult:
    """Line-of-sight computation result."""

    has_los: bool
    range_km: float
    cover_factor: float        # 0.0 = open, 1.0 = completely concealed


# ── Physics Engine ────────────────────────────────────────────────────────────
class PhysicsEngine:
    """
    Stateless physics calculator.

    All methods accept explicit inputs and return value objects; no side-effects.
    Injected with a TerrainEngine, SensorModel, and CommunicationModel so that
    they remain independently testable and replaceable.
    """

    def __init__(
        self,
        terrain: TerrainEngine,
        sensor_model: SensorModel | None = None,
        comms_model: CommunicationModel | None = None,
        fuel_reserve_threshold: float = 0.20,
        ammo_reserve_threshold: float = 0.10,
    ) -> None:
        self.terrain = terrain
        self.sensor = sensor_model or SensorModel()
        self.comms = comms_model or CommunicationModel()
        self.fuel_reserve_threshold = fuel_reserve_threshold
        self.ammo_reserve_threshold = ammo_reserve_threshold

    # ── Movement physics ──────────────────────────────────────────────────────
    def compute_movement(
        self,
        entity_type: str,
        origin: tuple[int, int],
        destination: tuple[int, int],
        current_fuel: float,
        weather_factor: float,
        load_factor: float = 1.0,
        lighting_factor: float = 1.0,
    ) -> MovementResult:
        """
        Compute physical movement from *origin* to *destination*.

        Returns a MovementResult which the caller uses to construct a
        MovementEvent and a FuelEvent.  Never mutates state.
        """
        cell = self.terrain.cell_at(origin)

        # Impassable check before anything else.
        if cell.has_river and not cell.has_bridge:
            return MovementResult(
                speed_kmh=0.0,
                travel_time_min=float("inf"),
                fuel_consumed=0.0,
                fuel_remaining=current_fuel,
                reserve_breach=False,
                road_used=False,
                terrain_type="RIVER_BLOCKED",
                impassable=True,
            )

        base_speed = _BASE_SPEED_KMH.get(entity_type, _BASE_SPEED_KMH["DEFAULT"])
        speed = self.terrain.movement_speed_kmh(
            base_speed_kmh=base_speed,
            position=origin,
            weather_factor=weather_factor,
            load_factor=load_factor,
            lighting_factor=lighting_factor,
        )

        # Distance in km: treat each grid step as 1 km.
        dx = abs(destination[0] - origin[0])
        dy = abs(destination[1] - origin[1])
        distance_km = sqrt(dx ** 2 + dy ** 2)

        travel_time_min = (distance_km / speed * 60.0) if speed > 0 else float("inf")

        fuel_rate = _FUEL_RATE_PER_KM.get(entity_type, _FUEL_RATE_PER_KM["DEFAULT"])
        # Apply terrain penalty to fuel consumption.
        terrain_penalty = 1.0 + max(0.0, 1.0 - cell.trafficability) * 0.5
        fuel_consumed = fuel_rate * distance_km * terrain_penalty
        fuel_remaining = max(0.0, current_fuel - fuel_consumed)
        reserve_breach = fuel_remaining < self.fuel_reserve_threshold

        terrain_type = self._classify_terrain(cell)

        return MovementResult(
            speed_kmh=round(speed, 2),
            travel_time_min=round(travel_time_min, 3),
            fuel_consumed=round(fuel_consumed, 5),
            fuel_remaining=round(fuel_remaining, 5),
            reserve_breach=reserve_breach,
            road_used=cell.has_road,
            terrain_type=terrain_type,
            impassable=False,
        )

    # ── LOS / Visibility ──────────────────────────────────────────────────────
    def compute_los(
        self,
        observer_pos: tuple[int, int],
        target_pos: tuple[int, int],
        weather_visibility: float = 1.0,
    ) -> LOSResult:
        """
        Approximate line-of-sight using grid geometry and terrain cover.

        In a full production system this would query a pre-computed LOS grid.
        Here we use terrain cover and range as a practical proxy.
        """
        observer_cell = self.terrain.cell_at(observer_pos)
        target_cell = self.terrain.cell_at(target_pos)

        dx = abs(target_pos[0] - observer_pos[0])
        dy = abs(target_pos[1] - observer_pos[1])
        range_km = sqrt(dx ** 2 + dy ** 2)

        # Average cover along the line.
        avg_cover = (
            self.terrain.terrain_cover(observer_pos)
            + self.terrain.terrain_cover(target_pos)
        ) / 2.0

        # Elevation advantage.
        elev_advantage = observer_cell.elevation_m - target_cell.elevation_m
        elev_factor = min(1.1, max(0.8, 1.0 + elev_advantage / 5000.0))

        # LOS degrades with range, cover, and poor weather.
        los_probability = (
            max(0.0, 1.0 - range_km / 15.0)
            * (1.0 - avg_cover * 0.7)
            * weather_visibility
            * elev_factor
        )
        has_los = los_probability > 0.15

        return LOSResult(
            has_los=has_los,
            range_km=round(range_km, 3),
            cover_factor=round(avg_cover, 3),
        )

    # ── Sensor detection ──────────────────────────────────────────────────────
    def compute_detection(
        self,
        observer_pos: tuple[int, int],
        target_pos: tuple[int, int],
        weather_effectiveness: float,
        ew_degradation: float,
        rng: random.Random,
    ) -> tuple[bool, float, float, float]:
        """
        Resolve whether *observer* detects *target*.

        Returns (detected, probability, terrain_cover_factor, effective_weather).
        """
        los = self.compute_los(observer_pos, target_pos, weather_effectiveness)
        cover = self.terrain.terrain_cover(target_pos)

        effective_weather = max(0.0, weather_effectiveness - ew_degradation)
        result = self.sensor.detect(
            distance_km=los.range_km,
            weather_effectiveness=effective_weather,
            terrain_cover=cover,
            rng=rng,
        )
        return result.detected, result.probability, cover, effective_weather

    # ── Engagement physics ────────────────────────────────────────────────────
    def compute_engagement(
        self,
        attacker_pos: tuple[int, int],
        target_pos: tuple[int, int],
        weapon_type: str,
        attacker_health: float,
        current_ammo: float,
        weather_effectiveness: float,
        target_in_cover: bool,
        rng: random.Random,
        roe_constraints: set[str] | None = None,
    ) -> EngagementResult:
        """
        Resolve a combat engagement including ROE compliance check.
        """
        if current_ammo <= 0:
            return EngagementResult(0.0, False, 0.0, False, True)

        max_range, base_hit = _WEAPON_PARAMS.get(
            weapon_type, _WEAPON_PARAMS["DEFAULT"]
        )
        los = self.compute_los(attacker_pos, target_pos, weather_effectiveness)
        if not los.has_los or los.range_km > max_range:
            return EngagementResult(0.0, False, 0.0, False, True)

        range_factor = max(0.1, 1.0 - los.range_km / max_range)
        cover_factor = max(0.2, 1.0 - los.cover_factor * 0.6) if target_in_cover else 1.0
        health_factor = max(0.5, attacker_health)   # degraded fire from wounded
        weather_factor = max(0.5, weather_effectiveness)

        hit_prob = min(0.95, base_hit * range_factor * cover_factor * health_factor * weather_factor)
        result_casualty = rng.random() < hit_prob
        ammo_consumed = min(current_ammo, 0.05)
        suppression = rng.random() < (hit_prob * 0.7)

        # ROE check: if "NO_FIRE_ZONE" is set we mark as non-compliant.
        roe_compliant = "NO_FIRE_ZONE" not in (roe_constraints or set())

        return EngagementResult(
            hit_probability=round(hit_prob, 4),
            result_casualty=result_casualty,
            ammo_consumed=ammo_consumed,
            suppression=suppression,
            roe_compliant=roe_compliant,
        )

    # ── Communications quality ────────────────────────────────────────────────
    def compute_comms(
        self,
        sender_pos: tuple[int, int],
        recipient_pos: tuple[int, int],
        baseline_quality: float,
        weather_quality: float,
        ew_interference: float,
        rng: random.Random,
    ) -> tuple[bool, float]:
        """
        Resolve communications link delivery and quality.

        Returns (delivered, link_quality).
        """
        dx = abs(recipient_pos[0] - sender_pos[0])
        dy = abs(recipient_pos[1] - sender_pos[1])
        distance_km = sqrt(dx ** 2 + dy ** 2)
        terrain_obstruction = self.terrain.terrain_cover(sender_pos)

        result = self.comms.transmit(
            baseline_quality=baseline_quality,
            distance_km=distance_km,
            terrain_obstruction=terrain_obstruction,
            weather_quality=weather_quality,
            ew_interference=ew_interference,
            rng=rng,
        )
        return result.delivered, round(result.quality, 4)

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _classify_terrain(cell: Any) -> str:
        if cell.elevation_m > 4000:
            return "HIGH_ALTITUDE"
        if cell.has_river:
            return "RIPARIAN"
        if cell.vegetation_density > 0.7:
            return "FOREST"
        if cell.has_road:
            return "ROAD"
        if cell.slope_degrees > 20:
            return "STEEP_GRADIENT"
        return "PLAINS"
