"""Extendable terrain abstraction; DEM import is intentionally deferred."""
from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians
from collections import deque
from typing import Iterable


@dataclass(frozen=True)
class TerrainCell:
    """A cell containing the Phase 2 terrain layers relevant to movement."""

    x: int
    y: int
    elevation_m: float = 0.0
    slope_degrees: float = 0.0
    trafficability: float = 1.0
    vegetation_density: float = 0.0
    has_road: bool = False
    has_river: bool = False
    has_bridge: bool = False
    chokepoint: bool = False
    cover: float = 0.0
    soil_factor: float = 1.0


@dataclass
class TerrainEngine:
    """Provides movement costs now and a stable boundary for future DEM rasters."""

    cells: dict[tuple[int, int], TerrainCell] = field(default_factory=dict)

    def load_cells(self, cells: Iterable[TerrainCell]) -> None:
        self.cells = {(cell.x, cell.y): cell for cell in cells}

    def cell_at(self, position: tuple[int, int]) -> TerrainCell:
        return self.cells.get(position, TerrainCell(*position))

    def movement_speed_kmh(self, base_speed_kmh: float, position: tuple[int, int], weather_factor: float = 1.0, load_factor: float = 1.0, lighting_factor: float = 1.0) -> float:
        """Apply the documented trafficability, slope, weather, load and lighting model."""
        cell = self.cell_at(position)
        if cell.has_river and not cell.has_bridge:
            return 0.0
        road_factor = 1.15 if cell.has_road else 1.0
        slope_factor = max(.15, cos(radians(min(abs(cell.slope_degrees), 80))))
        vegetation_factor = max(.35, 1 - cell.vegetation_density * .45)
        elevation_factor = max(.65, 1 - max(0.0, cell.elevation_m - 3000) / 20000)
        chokepoint_factor = .8 if cell.chokepoint else 1.0
        return max(0.0, base_speed_kmh * cell.trafficability * cell.soil_factor * slope_factor * vegetation_factor * elevation_factor * chokepoint_factor * road_factor * weather_factor * load_factor * lighting_factor)

    def movement_cost(self, distance_km: float, base_speed_kmh: float, position: tuple[int, int], **factors: float) -> float:
        """Return travel time in minutes; impassable terrain returns infinity."""
        speed = self.movement_speed_kmh(base_speed_kmh, position, **factors)
        return float("inf") if speed <= 0 else distance_km / speed * 60

    def import_dem(self, _source: str) -> None:
        """Import is delegated to the configured GIS service in later deployment layers."""
        raise ValueError("Use load_cells() with GIS/DEM-derived TerrainCell records")

    def terrain_cover(self, position: tuple[int, int]) -> float:
        """Return the combined concealment factor used by sensors and engagements."""
        cell = self.cell_at(position)
        return min(1.0, max(0.0, max(cell.cover, cell.vegetation_density * .7)))

    def route(self, start: tuple[int, int], destination: tuple[int, int]) -> list[tuple[int, int]]:
        """Find a passable four-neighbour route across the loaded terrain grid."""
        if start == destination:
            return [start]
        frontier: deque[tuple[int, int]] = deque([start])
        previous: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        while frontier:
            current = frontier.popleft()
            for offset in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                candidate = (current[0] + offset[0], current[1] + offset[1])
                if candidate in previous or candidate not in self.cells:
                    continue
                cell = self.cell_at(candidate)
                if cell.has_river and not cell.has_bridge:
                    continue
                previous[candidate] = current
                if candidate == destination:
                    path = [candidate]
                    while previous[path[-1]] is not None:
                        path.append(previous[path[-1]])
                    return list(reversed(path))
                frontier.append(candidate)
        return []
