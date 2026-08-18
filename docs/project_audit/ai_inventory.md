# AI Inventory

## 1. HTN Planner
- **Source file**: `services/planning-svc/htn/planner.py`, `services/planning-svc/htn/domain.py`
- **Public API**: Internal to Planning Service
- **Dependencies**: Rules Engine, Constraint Solver
- **Inputs**: Mission objectives, constraints, world state
- **Outputs**: Hierarchical task networks
- **Current status**: Partially implemented, functional
- **Integrated**: Yes, in `planning-svc`

## 2. Rule Engine
- **Source file**: `services/planning-svc/rules/engine.py`
- **Public API**: Internal to Planning Service
- **Dependencies**: Mission domain rules
- **Inputs**: Current state, proposed task
- **Outputs**: Precondition checks, rule execution results
- **Current status**: Functional (RETE algorithm concepts)
- **Integrated**: Yes

## 3. Bayesian Network
- **Source file**: `services/threat-svc/bayesian/network.py`
- **Public API**: Exposed via `/threats/assess`
- **Dependencies**: `pgmpy`
- **Inputs**: Sensor observations, environmental factors
- **Outputs**: Probability distributions of threats
- **Current status**: Implemented
- **Integrated**: Yes, in `threat-svc`

## 4. Knowledge Graph (GNN Reasoner)
- **Source file**: `services/kg-svc/main.py`, `services/kg-svc/seed_graph.py`
- **Public API**: `/kg/reasoning/{mission_id}`, `/kg/query`
- **Dependencies**: Neo4j, PyTorch (planned for GNN)
- **Inputs**: Graph queries, mission contexts
- **Outputs**: Reasoning paths, entity relationships
- **Current status**: Graph seeding and basic query implemented. GNN reasoning is a placeholder/mock.
- **Integrated**: Yes

## 5. Case-Based Reasoning (CBR)
- **Source file**: `services/planning-svc/cbr/engine.py`
- **Public API**: Internal to Planning Service
- **Dependencies**: FAISS (for vector similarity)
- **Inputs**: Current mission state
- **Outputs**: Similar past missions, ranked methods
- **Current status**: Implemented mock/basic similarity
- **Integrated**: Yes

## 6. Constraint Solver (ACO)
- **Source file**: `services/planning-svc/constraint/aco.py`
- **Public API**: Internal to Planning Service
- **Dependencies**: Optimization libraries
- **Inputs**: Resources, tasks
- **Outputs**: Valid resource allocations
- **Current status**: Basic implementation
- **Integrated**: Yes

## 7. COA Generator
- **Source file**: `services/planning-svc/coa/generator.py`
- **Public API**: `/planning/coa/generate`
- **Dependencies**: HTN Planner
- **Inputs**: Mission request
- **Outputs**: List of COAs
- **Current status**: Implemented
- **Integrated**: Yes

## 8. Explanation Generator
- **Source file**: `services/planning-svc/coa/explanations.py`
- **Public API**: Attached to COA outputs
- **Dependencies**: None
- **Inputs**: COA traces, rule firings
- **Outputs**: Human-readable `ExplanationObject`
- **Current status**: Template-based implementation
- **Integrated**: Yes

## 9. Simulation & Monte Carlo
- **Source file**: `services/wargame-svc/monte_carlo/orchestrator.py`, `services/wargame-svc/simulation/engine.py`
- **Public API**: `/wargame/simulate`
- **Dependencies**: Mesa, SimPy, physics models
- **Inputs**: COA to simulate
- **Outputs**: Risk distributions, simulation logs
- **Current status**: Implemented
- **Integrated**: Yes

## 10. Scoring
- **Source file**: `services/wargame-svc/simulation/scoring.py`
- **Public API**: Internal to Wargame Service
- **Dependencies**: Simulation outputs
- **Inputs**: Event logs, mission criteria
- **Outputs**: Final COA scores
- **Current status**: Implemented
- **Integrated**: Yes

## 11. Judge Agent
- **Source file**: `services/wargame-svc/agents/behaviours.py` (part of multi-agent simulation)
- **Public API**: Internal
- **Dependencies**: Simulation engine
- **Inputs**: Simulation events
- **Outputs**: ROE compliance checks
- **Current status**: Basic implementation
- **Integrated**: Yes
