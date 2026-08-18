"""
BATMANSimulation — SimPy discrete-event core with Mesa spatial model.

Architecture
────────────
SimPy Environment  → controls simulation time exclusively
BattlefieldModel   → Mesa model; manages agent spatial layout and scheduler
EventDispatcher    → routes events to domain handlers; maintains event log
PhysicsEngine      → stateless physics calculations (movement, LOS, fuel)
WorldState         → single source of mutable battlefield state

Simulation loop
───────────────
1.  Each agent type runs as an independent simpy.Process generator.
2.  Agents call decide() → list[SimulationEvent].
3.  Events are dispatched → handlers mutate WorldState and may emit cascading events.
4.  Each cascading event is scheduled in SimPy with an appropriate timeout.
5.  JudgeAgent evaluates a snapshot each tick; never mutates state.
6.  MissionEndEvent is dispatched when any termination condition fires.
7.  SimulationLogger records the complete run for AAR and training data.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Generator

try:
    import simpy
    _SIMPY_AVAILABLE = True
except ImportError:
    _SIMPY_AVAILABLE = False
    simpy = None  # type: ignore[assignment]

from agents.battlefield import (
    AgentState,
    BattlefieldAgent,
    CivilianAgent,
    EnvironmentAgent,
    FriendlyAgent,
    JudgeAgent,
    ThreatAgent,
)
from agents.behaviours import ThreatBehaviourSelector
from simulation.dispatcher import EventDispatcher
from simulation.events import (
    CommunicationEvent,
    EngagementEvent,
    FuelEvent,
    LogisticsEvent,
    MissionEndEvent,
    MovementEvent,
    ObjectiveEvent,
    SimulationEvent,
    SimulationEventType,
    WeatherEvent,
)
from simulation.logger import AgentDecisionRecord, SimulationLogger
from simulation.mesa_model import BattlefieldModel
from simulation.physics import PhysicsEngine
from terrain.model import TerrainCell, TerrainEngine
from weather.model import WeatherModel, WeatherState
from comms.model import CommunicationModel
from logistics.model import LogisticsModel
from sensor.model import SensorModel

from .models import Mission, SimulationConfig, SimulationResult, WorldState


# ── Mutable simulation world state ────────────────────────────────────────────
@dataclass
class LiveWorldState:
    """
    Single source of truth for mutable battlefield state during a simulation run.

    All domain state (agent positions, resources, weather, comms, objectives)
    lives here. Handlers receive this object and mutate it. Agents read from it
    (read-only during decide()) via snapshot properties.
    """

    # ── Configuration refs ────────────────────────────────────────────────────
    terrain_engine: TerrainEngine = field(default_factory=TerrainEngine)
    weather_model: WeatherModel = field(default_factory=WeatherModel)
    comms_baseline: float = 0.95
    ew_level: float = 0.0

    # ── Agent states by id ────────────────────────────────────────────────────
    agent_states: dict[str, AgentState] = field(default_factory=dict)

    # ── Objectives ────────────────────────────────────────────────────────────
    objectives_completed: int = 0
    objectives_total: int = 1

    # ── Counters ──────────────────────────────────────────────────────────────
    constraint_violations: list[str] = field(default_factory=list)
    roe_violations: int = 0
    comms_failures: int = 0
    friendly_casualties: int = 0
    civilian_casualties: int = 0
    failure_modes: list[str] = field(default_factory=list)
    ammo_consumed: float = 0.0

    # ── Termination flag ──────────────────────────────────────────────────────
    terminated: bool = False
    termination_reason: str = "TIME_LIMIT"

    @property
    def weather_effects(self):                      # type: ignore[return]
        return self.weather_model.current_effects

    @property
    def snapshot(self) -> dict[str, Any]:
        """Read-only snapshot for JudgeAgent."""
        return {
            "objectives_completed": self.objectives_completed,
            "objectives_total": self.objectives_total,
            "constraint_violations": list(self.constraint_violations),
            "roe_events": self.roe_violations,
            "friendly_casualties": self.friendly_casualties,
            "friendly_count": sum(
                1 for st in self.agent_states.values() if "friendly" in st.agent_id
            ),
            "civilian_casualties": self.civilian_casualties,
        }


# ── _FallbackEnvironment for offline tests ────────────────────────────────────
class _FallbackEnvironment:
    """Minimal SimPy-compatible runner for offline unit tests."""

    def __init__(self) -> None:
        self.now = 0.0
        self._queue: list[Generator[Any, Any, None]] = []

    def process(self, gen: Generator[Any, Any, None]) -> None:
        self._queue.append(gen)

    def timeout(self, delay: float) -> float:
        return delay

    def run(self, until: float | None = None) -> None:
        max_steps = 20000
        steps = 0
        while self._queue and steps < max_steps:
            gen = self._queue[0]
            try:
                advance = float(next(gen))
                self.now = min(self.now + advance, until or float("inf"))
            except StopIteration:
                self._queue.pop(0)
            steps += 1


# ── BATMANSimulation ──────────────────────────────────────────────────────────
class BATMANSimulation:
    """
    Production-quality discrete-event war-game simulation for one COA run.

    Responsibilities
    ────────────────
    • Initialise all agents, models, dispatcher, and physics engine.
    • Register event handlers on the dispatcher.
    • Run each agent as a SimPy process.
    • Collect and return a structured SimulationResult + SimulationLog.
    """

    def __init__(
        self,
        mission: Mission,
        world_state: WorldState,
        coa: Any,
        terrain: TerrainEngine | None = None,
        weather: WeatherModel | None = None,
        config: SimulationConfig | None = None,
    ) -> None:
        self.mission = mission
        self.world_state_input = world_state
        self.coa = coa
        self.config = config or SimulationConfig()
        self.rng = random.Random(self.config.random_seed)

        # ── Terrain ───────────────────────────────────────────────────────────
        self.terrain_engine = terrain or TerrainEngine()
        if not self.terrain_engine.cells:
            self.terrain_engine.load_cells([
                TerrainCell(
                    x=0, y=0,
                    elevation_m=world_state.elevation_m,
                    slope_degrees=world_state.slope_degrees,
                    trafficability=world_state.trafficability,
                    vegetation_density=world_state.vegetation_density,
                )
            ])

        # ── Weather ───────────────────────────────────────────────────────────
        self.weather_model = weather or WeatherModel(
            world_state.initial_weather, self.rng
        )

        # ── Physics ───────────────────────────────────────────────────────────
        self.physics = PhysicsEngine(
            terrain=self.terrain_engine,
            sensor_model=SensorModel(),
            comms_model=CommunicationModel(),
        )

        # ── Live world state ──────────────────────────────────────────────────
        self.live = LiveWorldState(
            terrain_engine=self.terrain_engine,
            weather_model=self.weather_model,
            comms_baseline=world_state.comms_baseline,
            objectives_total=max(len(mission.objectives), 1),
        )

        # ── Mesa model ────────────────────────────────────────────────────────
        self.mesa_model = BattlefieldModel()

        # ── Agents ────────────────────────────────────────────────────────────
        self.friendly_agents: list[FriendlyAgent] = []
        self.threat_agents:   list[ThreatAgent] = []
        self.civilian_agents: list[CivilianAgent] = []
        self.environment_agent = EnvironmentAgent("environment", model=self.mesa_model)
        self.judge_agent = JudgeAgent(model=self.mesa_model)

        self._build_agents()
        self._assign_coa_tasks()

        # ── Dispatcher ────────────────────────────────────────────────────────
        self.dispatcher = EventDispatcher()
        self._register_handlers()

        # ── Logger ───────────────────────────────────────────────────────────
        self.sim_logger = SimulationLogger(
            mission_id=mission.mission_id,
            coa_id=getattr(coa, "coa_id", "unknown"),
            run_seed=self.config.random_seed or 0,
            max_duration_min=self.config.max_duration_minutes,
            friendly_count=self.config.friendly_count,
            threat_count=self.config.threat_count,
            terrain_type="SYNTHETIC",
            initial_weather=world_state.initial_weather,
        )

    # ── Agent construction ────────────────────────────────────────────────────
    def _build_agents(self) -> None:
        for i in range(self.config.friendly_count):
            aid = f"friendly-{i}"
            state = AgentState(
                agent_id=aid,
                position=(i, 0),
                resources={
                    "fuel": self.world_state_input.fuel_available,
                    "ammo": self.world_state_input.ammunition_available,
                },
                entity_type="WHEELED",
            )
            agent = FriendlyAgent(aid, model=self.mesa_model, state=state)
            self.friendly_agents.append(agent)
            self.live.agent_states[aid] = state
            self.mesa_model.register_agent(agent)
            self.mesa_model.place_agent(agent, (float(i), 0.0))

        for i in range(self.config.threat_count):
            tid = f"threat-{i}"
            state = AgentState(
                agent_id=tid,
                position=(5 + i, 5),
                entity_type="INFANTRY",
            )
            behaviour = ThreatBehaviourSelector.select(
                threat_probability=self.world_state_input.threat_probability,
                mission_type=self.mission.mission_type,
                terrain_type=self.world_state_input.terrain,
                objective_pos=(5, 5),
            )
            agent = ThreatAgent(
                tid,
                model=self.mesa_model,
                state=state,
                behaviour=behaviour,
                threat_probability=self.world_state_input.threat_probability,
            )
            self.threat_agents.append(agent)
            self.live.agent_states[tid] = state
            self.mesa_model.register_agent(agent)
            self.mesa_model.place_agent(agent, (float(5 + i), 5.0))

        for i in range(self.config.civilian_count):
            cid = f"civilian-{i}"
            state = AgentState(
                agent_id=cid,
                position=(3, 3 + i),
                entity_type="INFANTRY",
            )
            agent = CivilianAgent(cid, model=self.mesa_model, state=state)
            self.civilian_agents.append(agent)
            self.live.agent_states[cid] = state
            self.mesa_model.register_agent(agent)
            self.mesa_model.place_agent(agent, (3.0, float(3 + i)))

    def _assign_coa_tasks(self) -> None:
        hierarchy = (
            getattr(self.coa, "task_hierarchy", None)
            or (self.coa.get("task_hierarchy", {}) if isinstance(self.coa, dict) else {})
        )
        tasks = self._extract_tasks(hierarchy)
        if not tasks:
            tasks = [{"name": "DEFAULT_OBJECTIVE", "duration_min": 60}]

        declared_duration = getattr(self.coa, "estimated_duration_min", None) or sum(
            t["duration_min"] for t in tasks
        )
        raw_duration = sum(t["duration_min"] for t in tasks) or 1
        scale = declared_duration / raw_duration

        target_positions = [(5, 5), (8, 8), (10, 3)]
        for idx, task in enumerate(tasks):
            agent = self.friendly_agents[idx % len(self.friendly_agents)]
            target = target_positions[idx % len(target_positions)]
            agent.assign_task(
                name=task["name"],
                duration_min=task["duration_min"] * scale,
                target_pos=target,
            )

    @staticmethod
    def _extract_tasks(node: dict[str, Any]) -> list[dict[str, Any]]:
        if not node:
            return []
        if node.get("primitive"):
            return [{"name": node["name"], "duration_min": max(1, node.get("duration_min", 1))}]
        return [
            task
            for child in node.get("children", [])
            for task in BATMANSimulation._extract_tasks(child)
        ]

    # ── Handler registration ──────────────────────────────────────────────────
    def _register_handlers(self) -> None:
        self.dispatcher.register(SimulationEventType.MOVEMENT,      self._handle_movement)
        self.dispatcher.register(SimulationEventType.FUEL,          self._handle_fuel)
        self.dispatcher.register(SimulationEventType.ENGAGEMENT,    self._handle_engagement)
        self.dispatcher.register(SimulationEventType.COMMUNICATION, self._handle_communication)
        self.dispatcher.register(SimulationEventType.OBJECTIVE,     self._handle_objective)
        self.dispatcher.register(SimulationEventType.WEATHER,       self._handle_weather)
        self.dispatcher.register(SimulationEventType.LOGISTICS,     self._handle_logistics)
        self.dispatcher.register(SimulationEventType.MISSION_END,   self._handle_mission_end)

    # ── Handlers (state mutation lives here, nowhere else) ────────────────────
    def _handle_movement(self, event: MovementEvent, live: LiveWorldState) -> list[SimulationEvent]:
        state = live.agent_states.get(event.agent_id)
        if state:
            state.position = event.destination
            agent = next(
                (a for a in self.mesa_model.active_agents if a.unique_id == event.agent_id),
                None,
            )
            if agent:
                self.mesa_model.move_agent_to(agent, (float(event.destination[0]), float(event.destination[1])))
        return []

    def _handle_fuel(self, event: FuelEvent, live: LiveWorldState) -> list[SimulationEvent]:
        state = live.agent_states.get(event.agent_id)
        if state:
            state.resources["fuel"] = event.fuel_remaining
        if event.reserve_breach:
            live.constraint_violations.append("FUEL_RESERVE")
            live.failure_modes.append("FUEL_RESERVE_BREACH")
        return []

    def _handle_engagement(self, event: EngagementEvent, live: LiveWorldState) -> list[SimulationEvent]:
        if not event.roe_compliant:
            live.roe_violations += 1
            live.constraint_violations.append("ROE_VIOLATION")

        # Ammo consumption on the attacker.
        attacker_state = live.agent_states.get(event.agent_id)
        if attacker_state:
            old_ammo = attacker_state.resources.get("ammo", 1.0)
            new_ammo = max(0.0, old_ammo - event.ammo_consumed)
            attacker_state.resources["ammo"] = new_ammo
            live.ammo_consumed += event.ammo_consumed
            if new_ammo < 0.10:
                live.constraint_violations.append("AMMUNITION_RESERVE")

        # Casualty on the target.
        if event.result_casualty:
            target_state = live.agent_states.get(event.target_id)
            if target_state:
                target_state.health = max(0.0, target_state.health - 0.5)
                if target_state.health <= 0:
                    target_state.status = "CASUALTY"
                    if "friendly" in (event.target_id or ""):
                        live.friendly_casualties += 1
                        live.failure_modes.append("FRIENDLY_CASUALTY")
                    elif "civilian" in (event.target_id or ""):
                        live.civilian_casualties += 1
                        live.constraint_violations.append("CIVILIAN_SAFETY")
                        live.failure_modes.append("CIVILIAN_CASUALTY")
        return []

    def _handle_communication(self, event: CommunicationEvent, live: LiveWorldState) -> list[SimulationEvent]:
        if not event.delivered:
            live.comms_failures += 1
            if live.comms_failures >= 3:
                live.failure_modes.append("COMMUNICATION_DEGRADATION")
        return []

    def _handle_objective(self, event: ObjectiveEvent, live: LiveWorldState) -> list[SimulationEvent]:
        if event.objective_status == "ACHIEVED":
            live.objectives_completed += 1
            self.sim_logger.log_objective(event.time_min, event.objective_id, "ACHIEVED")
        elif event.objective_status == "FAILED":
            live.failure_modes.append(f"OBJECTIVE_FAILED:{event.objective_id}")
            self.sim_logger.log_objective(event.time_min, event.objective_id, "FAILED")
        return []

    def _handle_weather(self, event: WeatherEvent, live: LiveWorldState) -> list[SimulationEvent]:
        self.sim_logger.log_weather_tick(event.to_state)
        return []

    def _handle_logistics(self, event: LogisticsEvent, live: LiveWorldState) -> list[SimulationEvent]:
        if event.violation:
            live.constraint_violations.append(event.violation)
        return []

    def _handle_mission_end(self, event: MissionEndEvent, live: LiveWorldState) -> list[SimulationEvent]:
        live.terminated = True
        live.termination_reason = event.termination_reason
        return []

    # ── Agent process generators ──────────────────────────────────────────────
    def _agent_process(self, env: Any, agent: BattlefieldAgent) -> Generator[Any, Any, None]:
        """SimPy process: one agent acts on its own schedule."""
        while env.now < self.config.max_duration_minutes and not self.live.terminated:
            if not agent.is_active():
                break
            visible = [
                a for a in self.mesa_model.active_agents
                if a.unique_id != agent.unique_id
            ]
            events = agent.decide(
                time_min=float(env.now),
                world_state=self.live,
                visible_entities=visible,
                rng=self.rng,
            )
            for event in events:
                cascading = self.dispatcher.dispatch(event, self.live)
                # Cascading events are queued but not re-dispatched in the same tick.

            # Log agent decision.
            state = self.live.agent_states.get(agent.unique_id, agent.state)
            self.sim_logger.log_agent_decision(AgentDecisionRecord(
                time_min=float(env.now),
                agent_id=agent.unique_id,
                agent_type=type(agent).__name__,
                decision=state.decision_state,
                behaviour=getattr(agent, "_behaviour", type("", (), {"name": "N/A"})()).name
                          if isinstance(agent, ThreatAgent) else "N/A",
                position=state.position,
                health=state.health,
                fuel=state.resources.get("fuel", 0.0),
                ammo=state.resources.get("ammo", 0.0),
            ))

            # Yield a tick appropriate to the agent type.
            tick = self.config.tick_minutes
            yield env.timeout(tick)

    def _judge_process(self, env: Any) -> Generator[Any, Any, None]:
        """SimPy process: judge evaluates every tick."""
        while env.now < self.config.max_duration_minutes and not self.live.terminated:
            self.judge_agent.decide(
                time_min=float(env.now),
                world_state=self.live,
                visible_entities=[],
                rng=self.rng,
            )
            self._check_termination(float(env.now))
            yield env.timeout(self.config.tick_minutes)

    def _check_termination(self, now: float) -> None:
        """Evaluate termination conditions and dispatch MissionEndEvent if met."""
        if self.live.terminated:
            return

        all_friendly_done = all(
            (not a.assigned_tasks) for a in self.friendly_agents
        )
        all_friendly_casualties = all(
            st.status == "CASUALTY" for st in self.live.agent_states.values()
            if "friendly" in st.agent_id
        )
        obj_complete = self.live.objectives_completed >= self.live.objectives_total

        reason = None
        success = False

        if obj_complete and all_friendly_done:
            reason = "OBJECTIVES_COMPLETED"
            success = not self.live.constraint_violations
        elif all_friendly_casualties:
            reason = "FRIENDLY_FORCE_INEFFECTIVE"

        if reason:
            end_event = MissionEndEvent.create(
                time_min=now,
                termination_reason=reason,
                success=success,
                objectives_completed=self.live.objectives_completed,
                objectives_total=self.live.objectives_total,
                total_friendly_casualties=self.live.friendly_casualties,
                total_civilian_casualties=self.live.civilian_casualties,
            )
            self.dispatcher.dispatch(end_event, self.live)

    # ── Main run ──────────────────────────────────────────────────────────────
    def run(self) -> SimulationResult:
        """Execute the full simulation and return a canonical SimulationResult."""
        env = simpy.Environment() if _SIMPY_AVAILABLE else _FallbackEnvironment()

        # Spawn agent processes.
        all_agents: list[BattlefieldAgent] = (
            self.friendly_agents
            + self.threat_agents
            + self.civilian_agents
            + [self.environment_agent]
        )
        for agent in all_agents:
            env.process(self._agent_process(env, agent))
        env.process(self._judge_process(env))

        # Run until time limit (termination conditions fire internally via dispatcher).
        env.run(until=self.config.max_duration_minutes)

        duration = float(getattr(env, "now", self.config.max_duration_minutes))
        duration = min(duration, float(self.config.max_duration_minutes))

        live = self.live
        success = (
            live.termination_reason == "OBJECTIVES_COMPLETED"
            and not live.constraint_violations
            and live.friendly_casualties == 0
        )

        if not success and live.termination_reason == "TIME_LIMIT":
            live.failure_modes.append("MISSION_TIMEOUT")

        fuel_consumed = sum(
            self.world_state_input.fuel_available - st.resources.get("fuel", 0.0)
            for aid, st in live.agent_states.items()
            if "friendly" in aid
        )

        total_tasks = (
            sum(len(a.assigned_tasks) for a in self.friendly_agents)
            + live.objectives_completed
        )

        self.sim_logger.finalise(
            success=success,
            termination_reason=live.termination_reason,
            duration_min=duration,
            friendly_casualties=live.friendly_casualties,
            civilian_casualties=live.civilian_casualties,
            fuel_consumed=fuel_consumed,
            ammo_consumed=live.ammo_consumed,
            comms_failures=live.comms_failures,
            constraint_violations=live.constraint_violations,
            roe_violations=live.roe_violations,
            objectives_completed=live.objectives_completed,
            objectives_total=live.objectives_total,
            failure_modes=live.failure_modes,
        )

        return SimulationResult(
            mission_id=self.mission.mission_id,
            success=success,
            termination_reason=live.termination_reason,
            completion_time_min=duration,
            friendly_casualties=live.friendly_casualties,
            civilian_casualties=live.civilian_casualties,
            fuel_consumed=round(max(0.0, fuel_consumed), 4),
            communication_failures=live.comms_failures,
            constraint_violations=list(dict.fromkeys(live.constraint_violations)),
            objectives_completed=live.objectives_completed,
            objectives_total=total_tasks,
            failure_modes=list(dict.fromkeys(live.failure_modes)),
            event_log=self.dispatcher.event_log,
            weather_history=[tick["to_state"] for tick in self.dispatcher.event_log if tick.get("event_type") == "WEATHER"],
        )
