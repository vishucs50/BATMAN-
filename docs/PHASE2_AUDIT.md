# Phase 2 Architecture Compliance Audit

**Scope:** Phase 2 only — the War Gaming / Digital Twin implementation, assessed against `BATMAN_Architecture.md` sections 5.2, 8.3, 9.1–9.4, 13–14, and the Phase 2 roadmap in section 16.2.

**Audit method:** Static review of the current implementation and tests. This audit does not change production code. `BATMAN_Architecture.md` is currently located at the repository root rather than `docs/`, so that root file was used as the source of truth.

## Overall result

**Partially Implemented.** The repository has the prescribed Phase 2 module boundaries, SimPy/Mesa dependencies, typed simulation contracts, stochastic weather, configurable parallel batching, statistics, scoring, and a Phase 1-to-Phase 2 integration test. However, it is a simplified prototype rather than a compliant digital twin: movement is not simulated, terrain is not connected to task execution, the judge does not evaluate outcomes, and the Monte Carlo implementation lacks the specified uncertainty and sensitivity analysis.

| Phase 2 requirement | Status | Primary implementation |
| --- | --- | --- |
| 1. SimPy discrete-event simulation core | Partially Implemented | `services/wargame-svc/simulation/engine.py` |
| 2. Mesa multi-agent integration | Partially Implemented | `services/wargame-svc/agents/battlefield.py` |
| 3. Terrain physics model | Partially Implemented | `services/wargame-svc/terrain/model.py` |
| 4. Stochastic weather model | Partially Implemented | `services/wargame-svc/weather/model.py` |
| 5. Battlefield agent behaviour | Partially Implemented | `services/wargame-svc/agents/battlefield.py` |
| 6. Monte Carlo orchestrator | Partially Implemented | `services/wargame-svc/monte_carlo/orchestrator.py` |
| 7. Outcome statistics engine | Partially Implemented | `services/wargame-svc/simulation/statistics.py` |
| 8. COA scoring engine | Partially Implemented | `services/wargame-svc/simulation/scoring.py` |
| Required Phase 2 tests and pipeline integration | Partially Implemented | `tests/unit/test_phase_two.py` |

No Phase 2 deliverable is fully implemented against the complete architecture specification.

## 1. SimPy discrete-event simulation core

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/simulation/engine.py`, `services/wargame-svc/simulation/models.py`, `services/requirements-common.txt`.

The service declares `simpy==4.1.1`. `BATMANSimulation.run()` creates a `simpy.Environment`, starts a generator process, advances the simulation clock with `timeout()`, records events, executes primitive tasks extracted from the Phase 1 COA hierarchy, models threat contacts, consumes fuel, models communications failures, and terminates on completed tasks, force ineffectiveness, or time limit. `SimulationResult` captures the requested outcome fields.

It does **not** implement the section 9.2 event-queue architecture: there is no priority queue, typed event dispatcher, event handlers, or event-driven world-state update. The process is a fixed five-minute tick loop. The engine creates a terrain model but never calls it; agents never change position, so movement and continuous terrain physics are not simulated. Logistics only consumes fuel; ammunition and other resources are not consumed. Communications are a single random threshold, not the specified RF propagation model. Sensor/detection surfaces are absent. The `Mission` and `WorldState` are local reduced dataclasses rather than adapters for the Phase 1 mission/world-state interfaces. A fallback scheduler is used if SimPy is unavailable, which is useful for offline tests but does not satisfy a production SimPy runtime.

**Missing functionality:** typed event queue and dispatch table; movement events and positional updates; terrain integration; RF, sensor, and richer logistics models; use of the canonical Phase 1 mission/world-state contracts; explicit mission-objective evaluation.

## 2. Mesa multi-agent integration

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/agents/battlefield.py`, `services/wargame-svc/simulation/engine.py`, `services/requirements-common.txt`.

The Mesa dependency is declared, and `BattlefieldAgent` subclasses `mesa.Agent` when Mesa is installed. All five requested agent types exist. `AgentState` provides the required position, status, health, resources, visibility, and decision-state fields. `MesaScheduler.step()` activates registered friendly, threat, and civilian agents once per simulation tick.

The implementation does not use a Mesa `Model`, `BaseScheduler`/`RandomActivation`, data collector, grid/space, or Mesa lifecycle. `MesaScheduler` is a project-local loop, not Mesa scheduling. Environment and judge agents are called directly outside that scheduler. There is no independent movement or spatial interaction among agents.

**Missing functionality:** actual Mesa model/scheduler integration; spatial model; randomized/defined activation policy; Mesa data collection; scheduling environment and judge consistently with other agents.

## 3. Terrain physics model

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/terrain/model.py`.

`TerrainCell` models elevation, slope, trafficability, vegetation, roads, rivers, bridges, and chokepoints. `TerrainEngine.movement_speed_kmh()` correctly includes trafficability, slope, vegetation, road, weather, load, and lighting factors, and treats an unbridged river as impassable. `movement_cost()` exposes a usable extension point.

The model is not connected to any agent movement or task execution. Elevation is stored but does not affect the formula. Roads, rivers, bridges, and chokepoints are cell flags rather than a navigable road/infrastructure network. DEM import explicitly raises `NotImplementedError`, which is consistent with deferring raster input but means no importer abstraction exists yet. The architecture's derived layers (slope from DEM, vehicle-specific trafficability, LOS, RF propagation, cover/concealment, flood and avalanche risk) are absent.

**Missing functionality:** terrain-aware position/movement updates; road network routing; DEM importer interface/adapter; derived terrain layers; vehicle-type model; use of elevation, chokepoints, and cover in simulation outcomes.

## 4. Stochastic weather model

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/weather/model.py`, `services/wargame-svc/agents/battlefield.py`, `services/wargame-svc/simulation/engine.py`.

The model implements the required `CLEAR`, `RAIN`, `FOG`, `SNOW`, and `WIND` states using seeded Markov transitions. Every state has visibility, movement speed, sensor effectiveness, communications quality, and detection-probability effects. The environment agent advances weather each tick. Friendly task duration responds to the movement factor; threat contact probability uses detection probability; and the engine uses communication quality when sampling failures.

`sensor_effectiveness` is defined but never consumed by a sensor model. Weather modifies task progress rather than actual terrain movement. There is no weather input/synchronisation adapter for manually imported or physical-world weather, as described by the digital-twin concept.

**Missing functionality:** sensor coverage/detection model using sensor effectiveness; weather-aware terrain movement; weather ingestion interface and forecast uncertainty controls.

## 5. Battlefield agent behaviour

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/agents/battlefield.py`, `services/wargame-svc/simulation/engine.py`.

`FriendlyAgent` executes primitive tasks from the HTN/COA hierarchy, updates visibility and decision state, and consumes fuel. `ThreatAgent` independently samples contact behavior using a supplied threat probability. `EnvironmentAgent` updates weather. `CivilianAgent` maintains environmental visibility/state. `JudgeAgent` is observational only and does not modify state, which correctly respects the requested non-interference constraint.

Threat agents are not driven by Phase 1 threat-model behaviour data. Civilians do not move, encounter agents, or influence outcomes; civilian casualties are sampled after the run directly by the engine. Friendly agents do not move, engage, use ammunition, or react to communications failures. The judge only appends snapshots; it does not evaluate mission success, objectives, ROE/constraint violations, or civilian casualties. The engine itself decides success from task completion, fuel/civilian violations, and casualties.

**Missing functionality:** threat-library behaviour adapters; spatial movement and engagements; civilian encounter model; friendly contingency behavior; judge-owned evaluation rules for objectives, constraints, civilian harm, and ROE.

## 6. Monte Carlo orchestrator

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/monte_carlo/orchestrator.py`, `services/wargame-svc/simulation/statistics.py`.

`MonteCarloOrchestrator.run()` defaults to 500 runs and 16 configurable workers, creates independently seeded simulation configurations, supports dependency injection via `simulation_factory`, runs batches in parallel, and returns individual results plus aggregate statistics.

The architecture calls for a multiprocessing pool; this implementation uses `ThreadPoolExecutor`. More importantly, it does not explicitly sample uncertainty distributions for threat behavior, sensor detection, comms/EW reliability, or civilian encounters; only the seeded simulation's weather/contact/random checks vary. It does not run Sobol sensitivity analysis, identify drivers of variance, or enforce/measure the target performance budget. It does not offer an API that evaluates and ranks every COA as a batch; callers must loop over COAs.

**Missing functionality:** process-based parallel option; explicit uncertainty samplers; EW/comms and sensor uncertainty; Sobol/sensitivity analysis; execution-budget telemetry; batch evaluation API for a COA set.

## 7. Outcome statistics engine

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/simulation/statistics.py`, `services/wargame-svc/simulation/models.py`.

The statistics engine computes mission success rate, expected friendly casualties, casualty standard deviation, expected fuel usage, P05/P50/P95 completion times, communications-failure distribution, constraint-violation rate, top-five failure mode frequencies, and success distribution. This is materially better than averaging every field and aligns with the architecture's primary aggregation metrics.

It does not preserve full completion-time, fuel, casualty, civilian-casualty, or constraint distributions—only selected quantiles/counters. It reports a combined constraint-violation rate rather than a dedicated ROE violation probability. Objective completion is present in each result but is not aggregated. There is no sensitivity summary.

**Missing functionality:** ROE-violation rate; objective-completion distribution; civilian-casualty statistics; additional outcome distributions; sensitivity output.

## 8. COA scoring engine

**Status: Partially Implemented**

**Implementation:** `services/wargame-svc/simulation/scoring.py`.

The scorer uses the architecture's seven default weights: success (.35), casualties (.25), time (.15), resources (.10), risk (.08), ROE (.04), and flexibility (.03). It accepts per-call weight overrides, consumes simulated outcome statistics, accepts threat probability and constraint penalty inputs, emits an explanatory reason list, and ranks COAs by descending utility.

The utility inputs are simplified. Mission effectiveness is just success rate; risk concentration is approximated from one threat probability, violation rate, and casualty deviation; flexibility is only the inverse of failure-mode count. The variance penalty is casualty standard deviation divided by success probability rather than the architecture's `σ(outcome) / E(outcome)` over a defined outcome distribution. It does not consume objective-level outcomes, threat assessments, or Phase 1 constraints directly, and it does not integrate with the existing Phase 1 explanation object.

**Missing functionality:** formal metric normalization; objective/threat/constraint adapters; outcome-based variance penalty; explicit risk-concentration and recoverability measures; structured ExplanationObject integration.

## Tests and integration coverage

**Status: Partially Implemented**

**Implementation:** `tests/unit/test_phase_two.py`.

The test module covers terrain speed calculation, weather transition, a basic simulation run, Monte Carlo/statistics/scoring, failure-mode aggregation, and an integration chain from Phase 1 HTN/COA generation to Phase 2 Monte Carlo and ranking.

The tests do not independently test each battlefield agent, communications/logistics/engagement behavior, terrain routing or bridge/rivers, all weather effects, judge non-interference/evaluation, parallel worker behavior, statistical edge cases, or a genuine installed SimPy/Mesa execution path. No performance test validates 500 runs per COA or the architecture's time budget.

**Missing functionality:** dedicated unit tests for every agent type and simulation event; real SimPy/Mesa integration tests; uncertainty/sensitivity tests; worker and determinism tests; performance benchmark.

## Cross-cutting architecture gaps

- Section 9.1's digital-twin mappings are represented only as local scalar inputs. Infrastructure and sensor-network models are absent.
- Section 9.2's `comms_model`, `sensor_model`, and `logistics_model` are embedded as minimal random/fuel logic, not distinct components.
- The service has no `main.py` or port-8003 FastAPI surface despite the microservice map in section 14.1. This is an integration gap, although it was not named as a Phase 2 deliverable.
- Phase 2 does not implement AAR, dashboard, GNN, learning, or dynamic replanning. Those omissions are correct because they are explicitly out of scope for this phase.

## Recommended completion order

1. Make position and movement first-class simulation events, using `TerrainEngine` for every movement/task transit.
2. Replace the project-local agent loop with a Mesa `Model` and scheduler; attach a spatial model and agent event contracts.
3. Move objective, ROE, civilian, and constraint evaluation into `JudgeAgent`; retain its read-only relationship to simulation state.
4. Add separate RF/comms, sensor detection, and resource-consumption components, then sample their uncertainty explicitly in Monte Carlo runs.
5. Add sensitivity analysis and expand statistics before revising the scoring formula to consume those complete metrics.
6. Add real-runtime and performance tests after installing the declared SimPy and Mesa dependencies.
