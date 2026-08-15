"""
Mesa BattlefieldModel — owns the agent spatial registry and scheduler.

Mesa is used exclusively for:
  • Agent spatial management (ContinuousSpace for position tracking)
  • Agent registration and lifecycle
  • Activation ordering (BaseScheduler)

Mesa does NOT advance simulation time. SimPy exclusively controls the clock.
"""
from __future__ import annotations

from typing import Any

try:
    from mesa import Model
    import mesa as _mesa_pkg
    _MESA_VERSION = tuple(int(x) for x in _mesa_pkg.__version__.split(".")[:2])
    _MESA_3 = _MESA_VERSION >= (3, 0)
    if not _MESA_3:
        from mesa.time import BaseScheduler
    _MESA_AVAILABLE = True
except ImportError:
    _MESA_AVAILABLE = False
    _MESA_3 = False

    class Model:                        # type: ignore[no-redef]
        def __init__(self) -> None:
            pass


class _InternalScheduler:
    """Drop-in replacement for deprecated Mesa BaseScheduler."""

    def __init__(self) -> None:
        self._agents: list[Any] = []

    def add(self, agent: Any) -> None:
        self._agents.append(agent)

    def remove(self, agent: Any) -> None:
        if agent in self._agents:
            self._agents.remove(agent)

    @property
    def agents(self) -> list[Any]:
        return list(self._agents)


class ContinuousSpace:                  # type: ignore[no-redef]
    """Minimal continuous space shim (used when Mesa is not installed or Mesa 3.x)."""

    def __init__(self, x_max: float, y_max: float, torus: bool = False) -> None:
        self.x_max, self.y_max = x_max, y_max
        self._positions: dict[str, tuple[float, float]] = {}

    def place_agent(self, agent: Any, pos: tuple[float, float]) -> None:
        self._positions[agent.unique_id] = pos
        agent.pos = pos

    def move_agent(self, agent: Any, pos: tuple[float, float]) -> None:
        self._positions[agent.unique_id] = pos
        agent.pos = pos

    def get_neighbors(
        self, pos: tuple[float, float], radius: float, include_center: bool = True
    ) -> list[Any]:
        return []


class BattlefieldModel(Model):
    """
    Mesa Model that owns the agent spatial space and scheduler.

    The SimPy engine holds a reference to this model. When an agent moves
    the engine calls model.space.move_agent() to update the spatial index.
    The scheduler is activated by the engine at configurable intervals but
    never advances the simulation clock.
    """

    def __init__(
        self,
        grid_width: float = 20.0,
        grid_height: float = 20.0,
    ) -> None:
        super().__init__()
        self.space = ContinuousSpace(grid_width, grid_height, torus=False)
        self.scheduler = _InternalScheduler()

    def register_agent(self, agent: Any) -> None:
        """
        Add an agent to the internal scheduler.

        Mesa 3.x calls this automatically in Agent.__init__. For spatial
        placement, call place_agent separately.
        """
        if agent not in self.scheduler.agents:
            self.scheduler.add(agent)

    def place_agent(self, agent: Any, pos: tuple[float, float]) -> None:
        """Place agent at pos in the continuous space."""
        self.space.place_agent(agent, pos)

    def deregister_agent(self, agent: Any) -> None:
        """Remove a terminated agent from the scheduler."""
        self.scheduler.remove(agent)

    def move_agent_to(self, agent: Any, pos: tuple[float, float]) -> None:
        """Update agent position in the spatial index."""
        self.space.move_agent(agent, pos)

    @property
    def active_agents(self) -> list[Any]:
        """All currently scheduled agents."""
        return list(self.scheduler.agents)
