# BATMAN: Battlefield Analytics & Tactical Mission Assistance Network
## AI Execution Map & Technical Audit Document — v2.0
*Prepared for: External AI Review and Verification*
*Classification: UNCLASSIFIED — Academic / Research Purpose Only*

---

# 1. AI COMPONENT INVENTORY

| Component | Exact File Path | Class/Function | Input | Output | Called at Runtime? | Calling Service | Downstream Consumer |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HTN Planner** | `services/planning-svc/htn/planner.py` | `HTNPlanner.plan` | `mission_type` (str), `WorldState` | `Plan` object (hierarchy, final state, rule firings) | Yes | `COAGenerator` | `COAResponse` |
| **Rule Engine** | `services/planning-svc/rules/engine.py` | `RuleEngine.validate_plan` | `WorldState`, `List[Task]` | `dict` (validity status, rule violations, penalties, firings) | Yes | `COAGenerator` | `COAResponse` |
| **CBR Engine** | `services/planning-svc/cbr/engine.py` | `CaseBasedReasoner.retrieve` | Query `Case` vector | `List[Tuple[Case, float]]` (matching cases, similarity scores) | Yes | `COAGenerator` | `ExplanationGenerator` |
| **Bayesian Threat Network** | `services/threat-svc/bayesian/network.py` | `ThreatNetwork.assess` | `evidence` (dict of binary sensor/weather/TOD variables) | `ThreatAssessment` (probabilities, risk score) | Yes | `threat-svc/main.py` | Frontend API |
| **Knowledge Graph** | `services/kg-svc/main.py` | FastAPI endpoints | Cypher queries / Graph requests | JSON nodes and relationships | Yes | Frontend (via API Gateway) | Frontend UI (2D graph) |
| **GNN / BRN** | `services/kg-svc/main.py` | `/kg/reasoning/{mission_id}` | `mission_id` (UUID) | Mock success rates, risk distribution, and radar metrics | Yes | Frontend (via API Gateway) | Frontend Risk Radar |
| **Constraint Solver / ACO** | `services/planning-svc/constraint/aco.py` | `ConstraintOptimizer.optimize` | `List[Assignment]`, resource budgets | `OptimizationResult` (unit-task assignments, score) | **No** (Disconnected) | None | None |
| **COA Generator** | `services/planning-svc/coa/generator.py` | `COAGenerator.generate` | `mission_type` (str), `facts` (dict) | Sorted `List[COA]` (BOLD, BALANCED, CAUTIOUS) | Yes | `planning-svc/main.py` | `planning-svc` responses |
| **Explanation Generator** | `services/planning-svc/coa/explanations.py` | `ExplanationGenerator.generate` | `List[COA]`, threat assessments | `Explanation` object (primary reasons, confidence, sources) | Yes | `planning-svc/main.py` | `COAResponse` |
| **Simulation Engine** | `services/wargame-svc/simulation/engine.py` | `BATMANSimulation.run` | `Mission`, `WorldState`, `COA`, `SimulationConfig` | `SimulationResult` | Yes | `wargame-svc/main.py` | `MonteCarloOrchestrator` |
| **Monte Carlo Orchestrator** | `services/wargame-svc/monte_carlo/orchestrator.py` | `MonteCarloOrchestrator.run` | `COA`, `Mission`, `WorldState`, `runs` | `List[SimulationResult]`, `OutcomeStatistics` | Yes | `wargame-svc/main.py` | Frontend API |
| **Statistics Engine** | `services/wargame-svc/simulation/statistics.py` | `OutcomeStatisticsEngine.aggregate` | `List[SimulationResult]` | `OutcomeStatistics` | Yes | `MonteCarloOrchestrator` | `wargame-svc` responses |
| **Scoring Engine** | `services/wargame-svc/simulation/scoring.py` | `COAScoringEngine.score` | `COA`, `OutcomeStatistics` | `COAScore` (multi-factor utility break-down) | **No** (Disconnected) | None | None |
| **What-If Engine** | `services/wargame-svc/main.py` | `/wargame/whatif` | `WhatIfRequest` | Static delta outcomes | **No** (Dead endpoint) | None | None |
| **Judge Agent** | `services/wargame-svc/agents/battlefield.py` | `JudgeAgent.decide` | `LiveWorldState` | Evaluates termination thresholds | Yes | SimPy scheduler loop | Simulation Engine |
| **Learning Pipeline** | N/A (Theoretical) | N/A | N/A | N/A | **No** (Unimplemented) | None | None |

---

# 2. REAL vs MOCK CLASSIFICATION

### 1. HTN Planner
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Implements a standard depth-first HTN decomposition algorithm in Python. It does not use learned neural models, but executes a formal tree expansion.
*   **Responsible file**: `services/planning-svc/htn/planner.py` -> `HTNPlanner`

### 2. Rule Engine
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: A standard forward-chaining rules validator. Does not execute a full RETE network but processes lists of rule predicates iteratively.
*   **Responsible file**: `services/planning-svc/rules/engine.py` -> `RuleEngine`

### 3. Bayesian Threat Network
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Runs a deterministic Bayesian Inference Network using the `pgmpy` library. In environments where `pgmpy` is absent, it falls back to a mathematical likelihood calculation (`likelihood = sum(values.values()) / 4`).
*   **Responsible file**: `services/threat-svc/bayesian/network.py` -> `ThreatNetwork`

### 4. CBR Engine
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Processes queries through vector cosine similarity using the `faiss` library (falling back to `numpy.dot` if `faiss` is not installed).
*   **Responsible file**: `services/planning-svc/cbr/engine.py` -> `CaseBasedReasoner`

### 5. Knowledge Graph
*   **Classification**: `SYNTHETIC DATA`
*   **Rationale**: Acts as a queryable memory database. It connects to a real Neo4j container if running, or falls back to an in-memory `networkx.DiGraph` using static seed structures.
*   **Responsible file**: `services/kg-svc/main.py` & `seed_graph.py`

### 6. GNN / BRN (Battlefield Reasoning Network)
*   **Classification**: `MOCK / PLACEHOLDER`
*   **Rationale**: The GNN described in the architecture document (featuring graph attention and neighborhood aggregation) is not implemented. The endpoint returns values generated stochastically via `random.random()`.
*   **Responsible file**: `services/kg-svc/main.py` -> `get_gnn_reasoning`

### 7. Constraint Solver / ACO
*   **Classification**: `DISCONNECTED`
*   **Rationale**: The code contains a real Ant Colony Optimization meta-heuristic solver, but it is completely disconnected and never invoked by any API router or generator.
*   **Responsible file**: `services/planning-svc/constraint/aco.py` -> `ConstraintOptimizer`

### 8. COA Generator
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Programmatically invokes the HTN Planner three times using BOLD, BALANCED, and CAUTIOUS modifiers, checks rules, and applies a utility scoring equation.
*   **Responsible file**: `services/planning-svc/coa/generator.py` -> `COAGenerator`

### 9. Explanation Generator
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Calculates confidence mathematically and generates briefing card text based on active rule violation counts and CBR match sizes.
*   **Responsible file**: `services/planning-svc/coa/explanations.py` -> `ExplanationGenerator`

### 10. Simulation Engine (War Gaming)
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: A discrete-event model runner powered by `simpy` and spatial tracking classes representing a SimPy/Mesa integration.
*   **Responsible file**: `services/wargame-svc/simulation/engine.py` -> `BATMANSimulation`

### 11. Monte Carlo Orchestrator
*   **Classification**: `ALGORITHMIC BASELINE`
*   **Rationale**: Orchestrates parallel workers to execute multiple simulations, injecting random perturbations based on Beta and Gaussian distributions.
*   **Responsible file**: `services/wargame-svc/monte_carlo/orchestrator.py` -> `MonteCarloOrchestrator`

### 12. Simulation Scoring Engine
*   **Classification**: `DISCONNECTED`
*   **Rationale**: Implements the multi-factor utility scoring engine specified in the architecture document, but is completely disconnected from the active runtime execution path (never called by the gateway or planning service).
*   **Responsible file**: `services/wargame-svc/simulation/scoring.py` -> `COAScoringEngine`

### 13. What-If Engine
*   **Classification**: `MOCK / PLACEHOLDER`
*   **Rationale**: The endpoint `/wargame/whatif` returns static, hardcoded JSON results.
*   **Responsible file**: `services/wargame-svc/main.py` -> `run_whatif`

---

# 3. ACTUAL EXECUTION TRACE

```
[Frontend CommandView UI]
       │ (User clicks "Generate COA")
       ▼
[Gateway API Proxy] (gateway/main.py)
       │ POST /api/v1/coa/generate
       ▼
[Gateway COA Router] (gateway/routers/coa.py)
       │ Proxies to planning-svc
       ▼
[Planning Service Main] (planning-svc/main.py:generate_coa)
       │ calls
       ▼
[COA Generator] (coa/generator.py:generate)
       ├─► [CBR Engine] (cbr/engine.py:retrieve)
       │     └─► Encodes query -> queries FAISS -> returns top matches
       ├─► [HTN Planner] (htn/planner.py:plan)
       │     └─► Decomposes root task -> calls domain methods (htn/mission_domains.py)
       │           └─► Validates primitive tasks against rules (rules/engine.py:validate_task)
       └─► Computes utility score -> returns list of COAs (BOLD, BALANCED, CAUTIOUS)
       │
       ▼
[Explanation Generator] (coa/explanations.py:generate)
       │ Derives recommended COA, computes confidence -> compiles brief
       ▼
[Planning Service Response]
       │ Returns completed COAs and Explanations
       ▼
[Frontend UI]
```

#### Simulation Trace (User clicks "Run Wargame"):
```
[Frontend UI]
       │ (Dispatches simulateCOA action)
       ▼
[Gateway Simulation Router] (gateway/routers/simulation.py)
       │ POST /api/v1/simulation/simulate
       ▼
[Wargame Service Main] (wargame-svc/main.py:simulate_coa)
       │ spawns background task
       ▼
[Monte Carlo Orchestrator] (monte_carlo/orchestrator.py:run)
       │ loops N times in ProcessPoolExecutor
       ├─► Perturbs world state variables (comms, threat, weather)
       ├─► Spawns SimPy + Mesa instance (simulation/engine.py:BATMANSimulation)
       │     ├─► Steps agents tick-by-tick (decide -> dispatch events)
       │     └─► JudgeAgent checks termination rules
       └─► Aggregates results (simulation/statistics.py:OutcomeStatisticsEngine)
       │
       ▼
[Redis Publish Channel]
       │ Publishes progress update to websocket alerts
       ▼
[Frontend UI]
```

---

# 4. DATASETS / KNOWLEDGE BASES

### 1. HTN Planning Rules Dataset
*   **File**: `services/planning-svc/htn/mission_domains.py`
*   **Size**: 137 tasks across 3 mission domain definitions.
*   **Schema**: Nested dictionary layout mapping mission names to operational stages, task networks, subtask lists, durations, and resource parameters.
*   **Loading**: Imported at startup; instantiated inside the domain builder (`build_phase_one_domain()`).
*   **Transformation**: Converted to `Domain`, `Method`, and `Operator` class structures.
*   **Influence**: **Critical**. Directly structures the generated COA task hierarchies.

### 2. CBR Historical Database
*   **File**: `services/planning-svc/cbr/engine.py`
*   **Size**: 3,000 synthetic reference records.
*   **Schema**: List of `Case` dataclasses containing `mission_type`, `terrain`, `threat`, `resources`, `urgency`, `outcome`, `plan_skeleton`, and `lessons_learned`.
*   **Loading**: Loaded on startup via `cbr.index(CaseBasedReasoner.synthetic_seed_cases())` in `planning-svc/main.py`.
*   **Transformation**: Transformed into normalized 8-dimensional float32 arrays and indexed into FAISS.
*   **Influence**: **High**. Similarity scores determine match IDs and calculate recommended COA confidence metrics.

### 3. Doctrine Validation Rules
*   **File**: `services/planning-svc/rules/engine.py`
*   **Size**: 60 doctrine rule objects.
*   **Schema**: `Rule` dataclass instance containing ID, text description, predicate callback, hard/soft classification, and penalty scores.
*   **Loading**: Imported at startup and loaded into the rule engine instance.
*   **Transformation**: Evaluated dynamically as logical assertions during HTN search steps.
*   **Influence**: **High**. Triggers plan invalidation or soft utility penalties.

### 4. Knowledge Graph Dataset
*   **File**: `services/kg-svc/seed_graph.py`
*   **Size**: 200 nodes and connected relation edges.
*   **Schema**: Node IDs categorized as `Unit`, `Road`, `TerrainFeat`, `Bridge`, `Sensor`, `ThreatActor`, `MissionObj`, `SupplyDepot`, or `ObservationPost`.
*   **Loading**: Loaded on startup to seed Neo4j or to instantiate an in-memory fallback networkx object.
*   **Transformation**: Populated into a `networkx.DiGraph` or Neo4j server nodes.
*   **Influence**: **Medium**. Feeds the GNN reasoning route, which uses the count of `ThreatActor` nodes to calculate threat multipliers.

---

# 5. HARDCODED VALUES

| File | Function | Value / Behavior | Why it is Hardcoded | Affects User Output? |
| :--- | :--- | :--- | :--- | :--- |
| `planning-svc/coa/generator.py` | `COAGenerator.styles` | `BOLD` (dur: 0.85, risk: 0.78), `CAUTIOUS` (dur: 1.20, risk: 0.97) | Baseline style modifiers | **Yes**. Scales durations and utility values. |
| `wargame-svc/main.py` | `run_whatif` | Static deltas: `{"delta_success": -0.15, "delta_casualties": +4.5}` | Feature placeholder | **No** (Unused endpoint). |
| `kg-svc/main.py` | `get_gnn_reasoning` | `mission_success_probability`: random range [0.75, 0.90] | GNN engine is a stub | **Yes**. Populates dashboard success rate. |
| `kg-svc/main.py` | `get_gnn_reasoning` | `route_risk_distribution`: random floats | GNN engine is a stub | **Yes**. Populates route risk chart values. |

---

# 6. PHASE 1 AI VERIFICATION

*   **CBR Retrieval**: Valid. Encoding logic scales `mission_type`, `terrain`, `threat`, `resources`, `urgency`, and `outcome` variables into an 8D vector. Searches the 3,000 cases index and outputs matches like `["SYN-1649", "SYN-1152"]`.
*   **HTN Decomposition**: Valid. The planner loops through nested tasks, matching operators to task states. Outputs a complete plan tree structure.
*   **Rule Evaluation**: Valid. Evaluated dynamically at task-generation time. Hard rules (like 3:1 force ratio) trigger `RuleViolation` backtracks; soft rules accumulate penalties.
*   **Bayesian Inference**: Valid. Runs a 5-node network (sensor quality, history, weather, TOD -> threat). In the fallback path, it uses a math equation representing likelihood.
*   **Knowledge Graph Reasoning**: Partially Mocked. While the graph nodes are loaded and queryable, the reasoning output (radar metrics, successor rate) is generated stochastically via `random.random()`.
*   **Constraint Evaluation**: Disconnected. The Ant Colony Optimization class (`ConstraintOptimizer`) is never called by the COA generator or planning endpoints.
*   **COA Generation & Scoring**: Valid. Programmatically generates BOLD, BALANCED, and CAUTIOUS postures and calculates utility via mathematical weighting.
*   **Explanation Generation**: Valid. Computes a briefing statement summarizing the primary choices, confidence rates, CBR case matches, and potential risks.

---

# 7. PHASE 2 INTELLIGENCE

Phase 2 introduces the digital twin war game simulator. 

*   **Trigger**: Clicking "Run Wargame" triggers `POST /api/v1/simulation/simulate`.
*   **Execution**:
    *   The `MonteCarloOrchestrator` spawns parallel runs.
    *   For each run, input variables are perturbed (e.g. comms quality receives Gaussian noise, weather changes stochastically based on transition weights, and threat behavior is selected dynamically).
    *   A `BATMANSimulation` instance is created, combining a SimPy environment and Mesa spatial grid.
    *   Infantry, threat, and environment agents execute tick-by-tick decisions, updating resource pools (fuel, ammo) and registering casualties.
    *   The statistics engine aggregates all results (quantiles, success rate, casualties).
*   **Feedback Limitation**: **No feedback loop**. The simulation results are returned to the frontend dashboard, but they **do not feed back** into the planning service or affect the generated COA utility scores. The COA utility scores are calculated statically in Phase 1 before simulation occurs.

---

# 8. PHASE 3 SYSTEM ANALYSIS

In Phase 3, dashboard panels display metrics fetched from the backend. The following table identifies which components are backed by real logic versus mocks:

| Dashboard Element | Source Backend Endpoint | Classification | Real Algorithm or Mock? |
| :--- | :--- | :--- | :--- |
| **COA List & Timeline** | `GET /api/v1/missions/{id}/coa` | `COAResponse` | **REAL**. Generated dynamically by HTN decomposition. |
| **Risk Factors Radar** | `GET /api/v1/kg/reasoning/{id}` | `GNNReasoningResponse` | **MOCK**. Uses `random.randint` to produce values. |
| **Success Probability** | `GET /api/v1/kg/reasoning/{id}` | `GNNReasoningResponse` | **MOCK**. Returns `random` floating-point value. |
| **Replay Events** | `GET /api/v1/simulation/simulations/{id}/replay` | `event_log` | **REAL**. Logged tick-by-tick from Mesa agents. |
| **Simulation Statistics** | `GET /api/v1/simulation/simulations/{id}` | `SimulationStatistics` | **REAL**. Aggregated over Monte Carlo SimPy runs. |
| **Route Risk Details** | `GET /api/v1/kg/reasoning/{id}` | `route_risk_distribution` | **MOCK**. Returns static random numbers. |

---

# 9. AI DEPENDENCY GRAPH

```mermaid
graph TD
    classDef real fill:#2a6,stroke:#153,color:#fff;
    classDef mock fill:#d55,stroke:#822,color:#fff;
    classDef disc fill:#aaa,stroke:#555,color:#fff;

    subgraph Phase 1 Planning
        MD["mission_domains.py (Dataset)"]::real --> HTN["HTNPlanner (Planner)"]::real
        RE["RuleEngine (Rules)"]::real --> HTN
        CBR["CaseBasedReasoner (CBR Database)"]::real --> COAG["COAGenerator (COA Core)"]::real
        HTN --> COAG
        COAG --> EXPG["ExplanationGenerator (XAI)"]::real
    end

    subgraph Threat & Graph
        TN["ThreatNetwork (Bayesian)"]::real --> ThreatAssess["GET /threats/missions/{id}"]::real
        KG["Neo4j / networkx (Graph)"]::real --> GNN["get_gnn_reasoning (BRN)"]::mock
    end

    subgraph Phase 2 Simulation
        SimPy["SimPy + Mesa (Physics engine)"]::real --> MC["MonteCarloOrchestrator"]::real
        MC --> Stats["OutcomeStatisticsEngine"]::real
    end

    subgraph Disconnected
        ACO["ConstraintOptimizer (ACO)"]::disc
        Scoring["COAScoringEngine (Scoring)"]::disc
    end

    %% Routing
    FrontendCommand[Frontend CommandView UI] -->|POST /coa/generate| COAG
    COAG -->|COAResponse| FrontendCommand
    FrontendCommand -->|GET /threats/missions/| ThreatAssess
    FrontendCommand -->|GET /kg/reasoning/| GNN
    FrontendCommand -->|POST /simulation/simulate| MC
```

---

# 10. END-TO-END EXAMPLE

This trace documents the execution of a `COUNTER_INFILTRATION` mission:

1.  **Mission Input**:
    *   `mission_type`: `"COUNTER_INFILTRATION"`
    *   `world_state`: `{"terrain": "FORESTED", "primary_threat": "INFILTRATION", "own_force": 9, "threat_strength": 2}`
2.  **CBR Retrieval**:
    *   Query is vectorized and evaluated against the database.
    *   Returns case matches: `["SYN-1649", "SYN-1152", "SYN-1474"]` (each referencing synthetic operational lessons).
3.  **HTN Tasks Decomposed**:
    *   `MISSION:COUNTER_INFILTRATION` resolves into:
        *   `Detect_and_Localise` -> `Deploy_Surveillance_Grid` (`POSITION_QRT`, `ACTIVATE_SENSOR_NETWORK`, `ESTABLISH_OBSERVATION_POSTS`, `DEPLOY_SEISMIC_SENSORS`, etc.)
        *   `Contain_and_Block` -> `Seal_Escape_Routes` (`IDENTIFY_CHOKEPOINTS`, `DEPLOY_BLOCKING_ELEMENTS`, etc.)
        *   `ROE_Compliant_Resolution` -> `Resolve_Threat` (`CLOSE_WITH_THREAT`, `APPLY_GRADUATED_FORCE`, etc.)
4.  **Fired Rules**:
    *   None (all preconditions like force ratio `9 >= 3 * 2` and cordon depth are satisfied by input facts).
5.  **Generated COAs**:
    *   `BALANCED`: Duration `873` minutes, utility score `0.5078`.
    *   `BOLD`: Duration `742` minutes, utility score `0.4851`.
    *   `CAUTIOUS`: Duration `1047` minutes, utility score `0.4632`.
6.  **Simulation / Monte Carlo Output** (When "Run Wargame" is triggered):
    *   Runs: `50`
    *   Success Rate: `62.0%`
    *   Expected Casualties: `0.38` (± `0.49` standard deviation)
    *   Expected Fuel Consumption: `0.0` (static wheeled base simulation)
    *   Constraint Violations: `["ROE_VIOLATION"]`
    *   Failure Modes: `["FRIENDLY_CASUALTY"]`
7.  **Final Dashboard Output**:
    *   COA Comparison Table displays the HTN plan graph.
    *   Risk Factors radar renders the mock indices (e.g. `Terrain: 64`, `Threat: 50`, `Logistics: 72`, `Comms: 81`, `Weather: 43`).

---

# 11. CURRENT AI MATURITY

| Component | Status | Evidence | Main Limitation |
| :--- | :--- | :--- | :--- |
| **HTN Planner** | `Production Baseline` | Correct decomposition of 137 subtasks in `mission_domains.py`. | Deterministic; requires manual domain authoring. |
| **Rule Engine** | `Production Baseline` | Processes all 60 rules and handles hard vs soft penalties. | Procedural evaluation; no reasoning optimization. |
| **CBR Engine** | `Production Baseline` | Queries 3,000 cases using vector embeddings via FAISS. | Relies on synthetic seed data; no active case retain loop. |
| **Bayesian Threat** | `Production Baseline` | Implements real 5-node DAG and variable elimination via `pgmpy`. | Inputs must be mapped manually to binary facts. |
| **GNN / BRN** | `Mock` | `random.random()` calls inside `kg-svc/main.py`. | **Does not run any neural network inference.** |
| **Constraint / ACO** | `Disconnected` | Class defined in `constraint/aco.py` but never imported or run. | **Plan generation does not optimize assignments using ACO.** |
| **Simulation / SimPy** | `Production Baseline` | Complete discrete-event agent step cycles and physics. | Static map dimensions; simplified engagement rules. |
| **Scoring / Wargame** | `Disconnected` | Class defined in `simulation/scoring.py` but never invoked. | **Simulation statistics do not update plan scoring.** |
| **Judge Agent** | `Production Baseline` | Monitors simulation ticks and triggers termination. | Hardcoded threshold rules. |
