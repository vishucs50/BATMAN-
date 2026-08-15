# BATMAN: Battlefield Analytics & Tactical Mission Assistance Network
## Technical Architecture & Design Document — v2.0

*Principal Defence Systems Architecture Proposal*
*Prepared for: SIH / VITISH Defence Innovation Hackathon*
*Classification Level: UNCLASSIFIED — Academic / Research Purpose Only*
*Date: August 2026*

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Strategic Vision & Design Philosophy](#2-strategic-vision--design-philosophy)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [Mission Planning Engine — Indigenous AI](#4-mission-planning-engine--indigenous-ai)
5. [AI Architecture](#5-ai-architecture)
6. [Indian Army Operational Profiles](#6-indian-army-operational-profiles)
7. [Threat Library](#7-threat-library)
8. [COA Generation Engine](#8-coa-generation-engine)
9. [War Gaming Engine — Digital Twin Simulation](#9-war-gaming-engine--digital-twin-simulation)
10. [Human-in-the-Loop Framework](#10-human-in-the-loop-framework)
11. [Command Dashboard](#11-command-dashboard)
12. [AI Learning & Continuous Improvement](#12-ai-learning--continuous-improvement)
13. [Technology Stack](#13-technology-stack)
14. [Software Architecture](#14-software-architecture)
15. [Database Design](#15-database-design)
16. [Development Roadmap](#16-development-roadmap)
17. [Innovation Features](#17-innovation-features)
18. [Risk Analysis & Critical Evaluation](#18-risk-analysis--critical-evaluation)
19. [Future Scope](#19-future-scope)
20. [Appendix: Algorithms Reference](#appendix-a-algorithms-reference)

---

# 1. EXECUTIVE SUMMARY

## 1.1 What is BATMAN?

**BATMAN — Battlefield Analytics & Tactical Mission Assistance Network** — is an indigenous, AI-powered **Command Decision Support System (CDSS)** designed for the Indian Armed Forces. It is **not** an autonomous weapons system. BATMAN operates entirely within a **Human-in-the-Loop (HITL)** framework: the AI plans, simulates, and explains; the human commander decides and commands.

BATMAN synthesizes four categories of intelligence into actionable, explainable decision support:

| Intelligence Category | What BATMAN Ingests | What BATMAN Produces |
|---|---|---|
| **Terrain & Environment** | GIS data, elevation, weather, infrastructure | Terrain-aware route scores, trafficability maps |
| **Threat Intelligence** | Sensor feeds, historical patterns, threat library | Dynamic threat probability maps, risk scores |
| **Own Force Status** | Unit positions, readiness, logistics, comms | Resource allocation plans, logistics forecasts |
| **Mission Knowledge** | Doctrine templates, past missions, COA history | Ranked COA options with full explanatory chains |

## 1.2 Core Design Principles

1. **Human Supremacy** — Every AI recommendation requires explicit commander authorization. No action is autonomous.
2. **Explainability First** — Every COA recommendation includes a full reasoning trace readable by a junior officer.
3. **Offline-First** — BATMAN operates in degraded, disconnected, intermittent, low-bandwidth (DDIL) environments. No external API dependency.
4. **Indigenous Intelligence** — All AI models are trained and operated on-premise. No dependency on GPT, Claude, Gemini, or any cloud LLM.
5. **Doctrine-Aligned** — BATMAN encodes Indian Army doctrinal templates, not NATO/US templates.
6. **Simulation-Driven** — Every COA is war-gamed before being presented to the commander.

## 1.3 What Makes BATMAN Different

| Feature | Traditional C2 Systems | BATMAN |
|---|---|---|
| COA Generation | Manual (hours) | AI-assisted (minutes) |
| War Gaming | Table-top exercises | Monte Carlo digital twin simulation |
| Explainability | None | Full structured reasoning trace |
| Learning | Static rules | Mission memory + offline model training |
| Terrain Analysis | 2D maps | 3D digital twin + trafficability AI |
| Threat Modelling | Fixed threat lists | Dynamic, probabilistic threat library |
| Human Control | Limited workflow | Full override + collaborative editing |

---

# 2. STRATEGIC VISION & DESIGN PHILOSOPHY

## 2.1 Design Philosophy

BATMAN is built around three philosophical anchors:

### Anchor 1: Decision Amplification, Not Decision Replacement
The Indian Army commander operates under extreme time pressure, cognitive load, and information overload. BATMAN's role is to collapse the **OODA loop** (Observe–Orient–Decide–Act) by automating the *Orient* phase — structuring available information into actionable options — while leaving *Decide* and *Act* entirely to the human.

### Anchor 2: Uncertainty as a First-Class Citizen
Classical C2 systems present plans as deterministic. BATMAN treats every battlefield variable as a **probability distribution**. Risk scores, timelines, and COA outcomes are presented with confidence intervals, not false precision.

### Anchor 3: Doctrine Encoded as Intelligence
Indian Army doctrine, tactical principles, Rules of Engagement (ROE), and mission planning frameworks are encoded directly into BATMAN's knowledge graph and rule engine — not approximated by a general-purpose LLM. This makes BATMAN's recommendations inherently doctrine-compliant and auditable.

## 2.2 Operational Envelope

```
SPECTRUM OF OPERATIONS
═══════════════════════════════════════════════════════════
HIGH INTENSITY ◄────────────────────────────► LOW INTENSITY
                    BATMAN OPERATIONAL ENVELOPE
  Border Defence │ Counter-Terror │ HADR │ Counter-Insurgency
  Conventional   │ Sub-conventional        │ Humanitarian
  War-fighting   │ Operations              │ Operations
═══════════════════════════════════════════════════════════
```

---

# 3. SYSTEM ARCHITECTURE OVERVIEW

## 3.1 High-Level Architecture

```
╔══════════════════════════════════════════════════════════════════════╗
║                    BATMAN SYSTEM ARCHITECTURE v2.0                   ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │                   PRESENTATION LAYER                         │    ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    ║
║  │  │Commander │ │ Intel    │ │Logistics │ │  AAR/Replay  │   │    ║
║  │  │Dashboard │ │ Console  │ │Dashboard │ │  Interface   │   │    ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                              │                                       ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │                   ORCHESTRATION LAYER                        │    ║
║  │              Mission Command Bus (Apache Kafka)              │    ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    ║
║  │  │ Session  │ │Decision  │ │Approval  │ │  Audit &     │   │    ║
║  │  │ Manager  │ │ Logger   │ │ Gateway  │ │  Compliance  │   │    ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                              │                                       ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │                   INTELLIGENCE LAYER                         │    ║
║  │                                                              │    ║
║  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │    ║
║  │  │ MISSION        │  │ WAR GAMING     │  │ THREAT       │  │    ║
║  │  │ PLANNING       │  │ ENGINE         │  │ ASSESSMENT   │  │    ║
║  │  │ ENGINE         │  │ (Digital Twin) │  │ MODULE       │  │    ║
║  │  │                │  │                │  │              │  │    ║
║  │  │ • HTN Planner  │  │ • MC Sim       │  │ • Risk Model │  │    ║
║  │  │ • COA Generator│  │ • Multi-Agent  │  │ • Threat KG  │  │    ║
║  │  │ • Constraint   │  │ • Terrain Sim  │  │ • Bayesian   │  │    ║
║  │  │   Solver (ACO) │  │ • Weather Sim  │  │   Estimator  │  │    ║
║  │  │ • CBR Engine   │  │ • AAR Engine   │  │              │  │    ║
║  │  └────────────────┘  └────────────────┘  └──────────────┘  │    ║
║  │                                                              │    ║
║  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │    ║
║  │  │ KNOWLEDGE      │  │ LOGISTICS &    │  │ SITUATION    │  │    ║
║  │  │ GRAPH ENGINE   │  │ RESOURCE MGR   │  │ AWARENESS    │  │    ║
║  │  │                │  │                │  │ FUSION       │  │    ║
║  │  │ • Mission KG   │  │ • Asset Tracker│  │              │  │    ║
║  │  │ • Doctrine KB  │  │ • Supply Chain │  │ • Sensor     │  │    ║
║  │  │ • GNN Reasoner │  │ • Readiness    │  │   Fusion     │  │    ║
║  │  │ • Rule Engine  │  │   Scoring      │  │ • Track Mgmt │  │    ║
║  │  └────────────────┘  └────────────────┘  └──────────────┘  │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                              │                                       ║
║  ┌─────────────────────────────────────────────────────────────┐    ║
║  │                        DATA LAYER                            │    ║
║  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    ║
║  │  │ PostGIS  │ │ Neo4j    │ │InfluxDB  │ │  Mission     │   │    ║
║  │  │ (GIS DB) │ │ (Graph)  │ │(TimeSer.)│ │  Memory      │   │    ║
║  │  │          │ │          │ │  /Redis  │ │  (MongoDB)   │   │    ║
║  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
╚══════════════════════════════════════════════════════════════════════╝
```

## 3.2 End-to-End Data Flow

```
SENSOR / INTEL FEEDS
        │
        ▼
┌───────────────────┐     ┌────────────────────┐
│  Situation        │────▶│  Threat Assessment  │
│  Awareness Fusion │     │  Module (Bayesian)  │
└───────────────────┘     └────────────────────┘
        │                          │
        ▼                          ▼
┌────────────────────────────────────────────┐
│          KNOWLEDGE GRAPH ENGINE             │
│    (Unified Battlefield Representation)     │
└────────────────────────────────────────────┘
        │
        ▼
┌───────────────────┐    ◄── COMMANDER INPUT
│  Mission Planning │        (type, constraints,
│  Engine (HTN)     │         objectives, weights)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  COA Generator    │──── generates ──▶  COA₁, COA₂, COA₃...COAₙ
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  War Gaming       │──── simulates each COA × N Monte Carlo runs
│  Engine           │──── produces risk distributions + failure modes
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  COA Scoring &    │──── ranks COAs by utility function
│  Ranking Engine   │──── generates structured explanations
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  HITL Interface   │──── COMMANDER REVIEWS, EDITS, APPROVES
└───────────────────┘
        │
        ▼
    MISSION EXECUTION  (external to BATMAN)
        │
        ▼
┌───────────────────┐
│  Mission Memory   │──── post-mission AAR feeds back into learning
│  & AAR Engine     │
└───────────────────┘
```

---

# 4. MISSION PLANNING ENGINE — INDIGENOUS AI

## 4.1 Why Not GPT / Claude / Gemini?

Large Language Models generate text that is *plausible* but not *provably correct*. For mission planning, every recommendation must be:

- **Traceable** to a specific knowledge source
- **Verifiable** against hard constraints (fuel, time, assets)
- **Explainable** in structured military language
- **Reproducible** given the same inputs
- **Operable offline** in a DDIL environment

LLMs satisfy none of these requirements reliably. BATMAN's planning intelligence is built on a **hybrid neuro-symbolic architecture** — combining structured symbolic reasoning (constraint satisfaction, rule engines, HTN planning) with learned neural models (GNNs, offline-trained scoring models).

## 4.2 Mission Representation (Extended PDDL+)

BATMAN uses an extended **Planning Domain Definition Language (PDDL+)** schema, augmented with probabilistic and temporal extensions for tactical operations.

### 4.2.1 Mission Object Model

```
MISSION := {
  mission_id:       UUID,
  mission_type:     MissionType,           // from MissionOntology
  classification:   SecurityLevel,
  objectives:       [Objective],           // ordered by priority
  constraints:      [Constraint],          // hard + soft
  resources:        [Resource],
  timeline:         TemporalWindow,
  aor:              AreaOfResponsibility,  // GIS polygon
  threat_context:   ThreatAssessment,
  roe:              [RulesOfEngagement],
  success_criteria: [SuccessCriterion]
}

OBJECTIVE := {
  id:       UUID,
  type:     ObjectiveType,  // SECURE|NEUTRALIZE|RESCUE|SURVEY|ESCORT
  target:   GeoEntity,
  priority: Integer [1..5],
  deadline: Timestamp,
  state:    ObjectiveState  // PENDING|ACTIVE|ACHIEVED|FAILED
}

CONSTRAINT := {
  type:      ConstraintType,   // HARD | SOFT
  category:  ConstraintCategory,
  // e.g., MAX_CASUALTIES, MIN_FORCE_RATIO, NO_FLY_ZONE,
  //        CURFEW_WINDOW, FUEL_LIMIT, COMMS_BLACKOUT
  predicate: LogicalExpression,
  penalty:   Float,            // for soft constraints in optimization
  violated:  Boolean
}
```

### 4.2.2 Battlefield World State (W)

The world state W is a 6-tuple:

```
W = ⟨ E, R, T, L, C, H ⟩

  E = Entity set     {friendly units, threats, civilians, infrastructure}
  R = Relation set   {positional, organizational, causal, temporal}
  T = Terrain state  {elevation, cover, trafficability, chokepoints}
  L = Logistics      {fuel, ammo, medical, comms, supply lines}
  C = Comms state    {link quality, net status, EW environment}
  H = Hazard state   {IED probability, threat zones, weather, NBC}
```

Each entity `Eᵢ` carries a typed state vector:

```
EntityState := {
  id:         UUID,
  type:       EntityType,
  position:   GeoPoint(lat, lon, alt),
  heading:    Float,
  speed:      Float,
  status:     ReadinessLevel,       // GREEN|AMBER|RED|BLACK
  payload:    [Capability],
  fuel:       Float [0..1],
  ammunition: Map<AmmoType, Integer>,
  comms:      CommStatus,
  timestamp:  Timestamp
}
```

## 4.3 State Space & Search Strategy

### 4.3.1 Hierarchical Task Network (HTN) Planning

BATMAN uses **HTN Planning** as its primary search strategy. HTN is particularly well-suited to military operations because:

1. Military missions are naturally hierarchical (campaign → operation → mission → task → sub-task)
2. Doctrinal templates map directly to HTN *methods*
3. HTN produces plans that decompose in a militarily interpretable way
4. HTN handles partial-order planning natively (concurrent task execution)

```
HTN DECOMPOSITION TREE — Counter-Infiltration Example
══════════════════════════════════════════════════════
MISSION: Counter_Infiltration_Response
│
├── OPERATION: Detect_and_Localise
│   ├── TASK: Deploy_Surveillance_Grid
│   │   ├── sub-task: Position_QRT_at_Waypoints
│   │   ├── sub-task: Activate_Sensor_Network
│   │   └── sub-task: Establish_Observation_Posts
│   └── TASK: Process_Sensor_Data
│       ├── sub-task: Correlate_Multi_Sensor_Feeds
│       └── sub-task: Track_and_ID_Infiltrators
│
├── OPERATION: Contain_and_Block
│   ├── TASK: Seal_Escape_Routes
│   │   ├── sub-task: Identify_Chokepoints (GIS)
│   │   └── sub-task: Deploy_Blocking_Elements
│   └── TASK: Establish_Cordon
│       └── sub-task: Grid_Square_Assignment
│
└── OPERATION: ROE_Compliant_Resolution
    ├── TASK: Close_With_Threat
    └── TASK: Apply_Graduated_Force
══════════════════════════════════════════════════════
```

### 4.3.2 HTN Algorithm Core

```python
class BATMANHTNPlanner:
    def __init__(self, domain: TacticalDomain, world_state: WorldState):
        self.domain = domain
        self.state = world_state
        self.rule_engine = domain.rule_engine
        self.cbr_engine = domain.cbr

    def plan(self, task_network: TaskNetwork) -> Optional[Plan]:
        """HTN planning with constraint propagation and CBR warm-start."""
        return self._seek_plan(self.state, task_network, Plan())

    def _seek_plan(self, state, task_net, plan):
        if task_net.is_empty():
            return plan  # success

        task = task_net.first_task()  # partial-order aware

        if task.is_primitive():
            # Gate 1: rule engine checks preconditions
            if not self.rule_engine.check_preconditions(state, task):
                return None
            # Gate 2: hard constraint check
            if self.violates_hard_constraint(state, task):
                return None
            new_state = self.apply_action(state, task)
            return self._seek_plan(new_state, task_net.rest(),
                                   plan.append(task))
        else:
            methods = self.domain.methods_for(task)
            # CBR ranks methods — likely-successful ones tried first
            methods = self.cbr_engine.rank_methods(methods, state, task)

            for method in methods:
                sub_network = method.decompose(task, state)
                merged = task_net.replace(task, sub_network)
                result = self._seek_plan(state, merged, plan)
                if result is not None:
                    return result

            return None  # backtrack

    def violates_hard_constraint(self, state, action):
        return any(c.predicate(state, action)
                   for c in self.mission.hard_constraints)
```

### 4.3.3 Constraint Hierarchy

```
CONSTRAINT HIERARCHY
══════════════════════════════════════════════
Layer 1 — ABSOLUTE (never violated)
  • Rules of Engagement (ROE)
  • Minimum force protection thresholds
  • No-fire zones / exclusion areas
  • Civilian safety perimeters

Layer 2 — DOCTRINAL (strong preference)
  • Force ratio minimums
  • Flanking depth requirements
  • Reserve force percentage
  • Comms architecture requirements

Layer 3 — RESOURCE (optimization targets)
  • Fuel budgets per unit
  • Ammunition load-out limits
  • Mission time windows
  • MEDEVAC radius constraints

Layer 4 — PREFERENCE (soft, weighted)
  • Minimize exposure time
  • Prefer covered approaches
  • Optimize for surprise
  • Minimize civilian disruption
══════════════════════════════════════════════
```

Layers 1–2 are checked symbolically at each HTN decomposition step (prune early). Layers 3–4 feed into the COA utility function for numeric optimization.

## 4.4 Tactical Reasoning Engine

### 4.4.1 Rule Engine (RETE Network)

BATMAN's rule engine uses forward-chaining production rules organized as **Tactical Rulesets** per mission type:

```
RULESET: Counter_Infiltration_Rules
────────────────────────────────────────────────────────────────────
RULE CI-001: Minimum Cordon Depth
  IF  mission.type == COUNTER_INFILTRATION
  AND terrain.type IN [FORESTED, MOUNTAINOUS]
  THEN cordon.min_depth = 500m
       cordon.min_elements = 3

RULE CI-002: Night Operations Degradation
  IF  time.period == NIGHT
  AND unit.has_NVD == FALSE
  THEN PENALISE(approach_speed, factor=0.5)
       ADD(risk_score, +15)

RULE CI-003: Weather → Helicopter Feasibility
  IF  weather.visibility < 500m
  OR  weather.wind_speed > 40 km/h
  THEN helicopter_ops.feasibility = LOW
       SUGGEST(ground_only_approach)

RULE CI-004: RF Shadow → Comms Relay
  IF  terrain.has_RF_shadow == TRUE
  AND distance_from_HQ > 20 km
  THEN REQUIRE(comms_relay_element)
       ADD(resource_requirement, RELAY_TEAM)
────────────────────────────────────────────────────────────────────
```

### 4.4.2 Bayesian Threat Estimation Network

```
THREAT ESTIMATION BAYESIAN NETWORK (simplified)
═════════════════════════════════════════════════
P(Infiltration | Sensor_Alert, Historical_Pattern, Weather, ToD)

       P(Sensor_Alert)    P(Historical_Pattern)
             │                      │
             ▼                      ▼
        ┌─────────┐           ┌──────────────┐
        │ Sensor  │           │   Pattern    │
        │ Quality │           │   Match      │
        └────┬────┘           └──────┬───────┘
             │                      │
             └──────────┬───────────┘
                        ▼
                ┌───────────────┐  ◄─ P(Weather_Favours_Mvmt)
                │  INFILTRATION │  ◄─ P(ToD_Favours_Mvmt)
                │  PROBABILITY  │
                └───────┬───────┘
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
    ┌────────────┐          ┌────────────────┐
    │   Route    │          │   Group Size   │
    │  Selection │          │   P(S | I)     │
    │  P(R | I)  │          └────────────────┘
    └────────────┘
═════════════════════════════════════════════════

Update rule (sequential sensor arrivals):
  P(T | E₁, E₂,...,Eₙ) ∝ P(T) × ∏ᵢ P(Eᵢ | T)
```

### 4.4.3 Case-Based Reasoning (CBR)

```
CBR CYCLE
═══════════════════════════════════════════════════════
1. RETRIEVE
   • Encode current mission as feature vector
   • Compute similarity against mission memory index
   • Return top-K similar historical cases

2. REUSE
   • Extract plan skeleton from retrieved case(s)
   • Adapt to current world state (constraint repair)
   • Seed HTN planner with adapted skeleton

3. REVISE
   • War-game the adapted plan
   • Identify failures; apply incremental repair
   • Produce validated plan

4. RETAIN
   • Store {mission, plan, outcome} as new case
   • Update similarity index (FAISS vector store)
═══════════════════════════════════════════════════════

SIMILARITY FUNCTION:
  sim(Cₐ, Cᵦ) =
      w₁ × geo_sim(aor_a, aor_b)          // terrain signature
    + w₂ × threat_sim(threats_a, threats_b) // threat type match
    + w₃ × resource_sim(assets_a, assets_b) // force composition
    + w₄ × objective_sim(obj_a, obj_b)     // mission objectives
    + w₅ × temporal_sim(T_a, T_b)          // time constraints

  Σ wᵢ = 1  (weights learned from retrieval quality feedback)
```

## 4.5 Knowledge Representation — Three Layers

### Layer 1: Mission Ontology (OWL 2)

```
BATMAN MISSION ONTOLOGY (partial)
═════════════════════════════════════════════════════════
MilitaryOperation
  ├── ConventionalOperation
  │   ├── BorderDefenceOp
  │   └── FireSupportOp
  ├── SubConventionalOperation
  │   ├── CounterInsurgencyOp
  │   ├── CounterTerrorismOp
  │   └── SpecialOpsOp
  │       ├── HostageRescueOp
  │       └── DeepReconOp
  └── HADROperation
      ├── FloodReliefOp
      ├── EarthquakeResponseOp
      └── EvacuationOp

MilitaryUnit
  ├── Infantry
  │   ├── RashtriyaRifles
  │   ├── PARA_SF
  │   └── Ghatak
  ├── Armour
  ├── Artillery
  ├── Aviation
  │   ├── ALH_Dhruv      // 7,000m ceiling
  │   └── Chetak
  └── Support
      ├── Engineers
      ├── Signals
      └── Medical

Terrain
  ├── Himalayan
  │   ├── HighAltitude   // >4,000m
  │   └── SubAlpine
  ├── PlainsTerrain
  ├── UrbanTerrain
  ├── RiparianTerrain
  └── DenseForestedTerrain

ThreatEntity
  ├── AsymmetricThreat
  │   ├── Infiltrator
  │   ├── IED
  │   └── TerroristGroup
  ├── ConventionalThreat
  │   ├── AdversaryUnit
  │   └── ArmedVehicle
  └── EmergingThreat
      ├── UAS
      │   ├── ReconUAV
      │   ├── DroneSwarm
      │   └── LoiteringMunition
      └── CyberThreat
═════════════════════════════════════════════════════════
```

### Layer 2: Knowledge Graph (Neo4j)

```
KNOWLEDGE GRAPH SCHEMA
══════════════════════════════════════════════════════
NODES:
  (Unit         {id, type, position, status, readiness})
  (ThreatActor  {id, type, location, probability, confidence})
  (TerrainFeat  {id, type, elevation, trafficability})
  (Infrastructure {id, type, criticality, condition})
  (MissionObj   {id, type, priority, status})
  (WeatherSys   {id, type, intensity, forecast})

EDGES:
  (Unit)-[:POSITIONED_AT]->(Location)
  (Unit)-[:ASSIGNED_TO]->(MissionObjective)
  (Unit)-[:COMMANDS]->(Unit)
  (ThreatActor)-[:THREATENS]->(Infrastructure)
  (ThreatActor)-[:LOCATED_IN]->(TerrainFeature)
  (TerrainFeature)-[:ADJACENT_TO]->(TerrainFeature)
  (Route)-[:PASSES_THROUGH]->(TerrainFeature)
  (Route)-[:HAS_RISK {probability}]->(ThreatActor)
  (Mission)-[:REQUIRES]->(Unit)
  (Mission)-[:TARGETS]->(MissionObjective)
══════════════════════════════════════════════════════
```

### Layer 3: Graph Neural Network (Battlefield Reasoning Network)

GNNs natively reason over relational structures. The risk of a route depends not just on its intrinsic properties but on the *interaction* between terrain, threat positions, own-force cover, and weather — a relational dependency that flat feature vectors cannot capture.

```
GNN ARCHITECTURE: Battlefield Reasoning Network (BRN)
══════════════════════════════════════════════════════
Input: G = (V, E, Xᵥ, Xₑ)
  V   = entity nodes
  E   = relationship edges
  Xᵥ  = node feature matrix [position, type, status, ...]
  Xₑ  = edge feature matrix [distance, risk, cover, ...]

Layer 1: Multi-head Graph Attention (8 heads)
  hᵥ⁽¹⁾ = σ( Σ_{u∈N(v)} αᵥᵤ W hᵤ⁽⁰⁾ )
  αᵥᵤ  = learned attention coefficient

Layer 2: Neighbourhood Aggregation
  hᵥ⁽²⁾ = f( hᵥ⁽¹⁾, AGGREGATE({hᵤ⁽¹⁾ : u∈N(v)}) )

Layer 3: Global Readout (graph-level)
  ĥ_G = READOUT({hᵥ⁽ᴸ⁾ : v∈V})

Output heads:
  • Mission Success Probability : sigmoid(MLP(ĥ_G))
  • Route Risk Distribution     : softmax(MLP(h_route⁽ᴸ⁾))
  • Critical Asset Score        : sigmoid(MLP(hᵥ⁽ᴸ⁾)) per asset v
══════════════════════════════════════════════════════
```

## 4.6 Resource Allocation (Multi-Dimensional Knapsack)

```
RESOURCE ALLOCATION FORMULATION

Maximize:   Σᵢ vᵢ × xᵢ          (total mission value)

Subject to:
  Σᵢ wᵢₖ × xᵢ ≤ Cₖ              ∀k  (resource type k capacity)
  xᵢ ∈ {0, 1}                   ∀i  (binary assignment)
  precedence(xᵢ, xⱼ)            (task ordering constraints)
  timing(xᵢ, tₛ, tₑ)            (temporal windows)

Resource types k ∈ {FUEL, AMMO, PERSONNEL, VEHICLES, MEDICAL, COMMS}

Solver: Ant Colony Optimization (ACO)
Target: near-optimal solution in < 60 seconds (P95 planning scenario)
```

## 4.7 Dynamic Replanning

```
REPLANNING TRIGGER SYSTEM
══════════════════════════════════════════════════
LEVEL 1 — ADVISORY (no plan change required)
  • Threat confidence shift > 10%
  • Weather deterioration warning
  • Minor logistics deviation
  → Commander notified; no action needed

LEVEL 2 — PLAN ADAPTATION (incremental replan)
  • New threat detected within AOR
  • Unit casualty requiring reassignment
  • Communication link failure
  • Time-critical threshold crossed
  → Replanning window: 3–5 min
  → Commander notification mandatory

LEVEL 3 — EMERGENCY REPLAN (full replan)
  • Multiple units compromised
  • Primary objective no longer achievable
  • Major threat escalation (category change)
  → Replanning window: 8–10 min
  → Commander approval mandatory before execution
══════════════════════════════════════════════════

ALGORITHM:
  1. Identify violated plan preconditions
  2. Compute minimal repair scope (affected HTN sub-tree)
  3. Run constrained HTN replan on that sub-tree
  4. War-game new sub-plan (reduced MC runs for speed)
  5. Generate delta-explanation ("Plan changed because…")
  6. Present to commander with urgency indicator
```

## 4.8 Explainability (XAI)

Every BATMAN recommendation produces a structured **Explanation Object**:

```
ExplanationObject := {
  decision:            String,       // "COA-2 is recommended"
  primary_reasons:     [ReasonChain], // top 3, each source-traced
  supporting_evidence: [Evidence],   // sensor data, cases cited
  rule_firings:        [RuleID],     // which rules fired
  cbr_matches:         [CaseID],     // similar past missions
  risk_factors:        [RiskFactor], // what makes this risky
  alternatives:        [COASummary], // why others scored lower
  confidence:          Float,        // 0..1
  uncertainty_sources: [String],     // known unknowns
  model_version:       String        // for audit traceability
}
```

The UI renders this as a **Commander's Briefing Card** — structured, plain-language, in Indian Army planning terminology.

---

# 5. AI ARCHITECTURE

## 5.1 Technique Selection Matrix

```
BATMAN AI ARCHITECTURE MAP
══════════════════════════════════════════════════════════════════
TECHNIQUE                  ROLE                        STATUS
──────────────────────────────────────────────────────────────────
HTN Planner                Primary planning engine       CORE
Rule Engine (RETE)         Constraint & doctrine         CORE
Bayesian Network           Threat probability            CORE
Case-Based Reasoning       Plan seeding, risk priming    CORE
Graph Neural Network (GAT) Relational battlefield reason CORE
Monte Carlo Simulation     COA war-gaming                CORE
Ant Colony Optimization    Resource allocation           CORE
Knowledge Graph (Neo4j)    Structured world knowledge    CORE
Mission Ontology (OWL 2)   Semantic interoperability     CORE
Multi-Agent Simulation     Entity behaviour in wargame   CORE
──────────────────────────────────────────────────────────────────
Reinforcement Learning     Adaptive planning weights     FUTURE v2
Deep RL (policy optim.)    End-to-end planning           FUTURE v3
Local Transformer (ONNX)   Offline report summarisation  FUTURE v2
──────────────────────────────────────────────────────────────────
NOT USED:
  External LLM APIs (GPT / Claude / Gemini)
  Reason: DDIL-incompatible, non-deterministic, non-auditable
  Computer Vision (live feeds) — out of scope for v1
══════════════════════════════════════════════════════════════════
```

## 5.2 Multi-Agent System in War Gaming

```
AGENT TAXONOMY
════════════════════════════════════════════════
FriendlyAgent
  • Follows HTN plan assignment
  • Handles local contingencies autonomously
    (route blocked → reroute within bounds)
  • Reports status events to simulation judge
  • Degrades realistically: fuel, ammo, morale model

ThreatAgent
  • Behaviour modelled from threat library
  • Uses adversarial planning heuristics
  • Reacts to own-force actions
  • Models: probe-fix-exploit, IED emplacement,
            drone patrol patterns, swarm coordination

EnvironmentAgent
  • Stochastic weather evolution
  • Terrain events (landslide, flash flood)
  • Infrastructure degradation

JudgeAgent
  • Evaluates ROE compliance per event
  • Scores outcomes against objectives
  • Records structured event log for AAR
════════════════════════════════════════════════
```

## 5.3 Simulation-Driven Learning Pipeline

```
LEARNING DATA PIPELINE
═══════════════════════════════════════════════════════════════
War Gaming Engine      Simulation Logs      Feature Extractor
(10,000+ runs/night) ─────────────────▶ (structured events) ──▶
                                                               │
                                                               ▼
                                                    Training Dataset
                                                   (plan → outcome)
                                                               │
                               ┌───────────────────────────────┤
                               │                               │
                               ▼                               ▼
                        GNN Training               HTN Heuristic
                        (outcome prediction)        Weight Update
                               │                               │
                               ▼                               ▼
                         Updated BRN              Updated Planner
                         Weights                  Heuristics
                               │                               │
                               └───────────────┬───────────────┘
                                               ▼
                                        Model Registry
                                        (versioned, evaluated,
                                         regression-tested)
═══════════════════════════════════════════════════════════════
```

---

# 6. INDIAN ARMY OPERATIONAL PROFILES

## 6.1 Cross-Border Infiltration Response

| Attribute | Detail |
|---|---|
| **Trigger** | IB/LOC sensor alert, patrol contact, human intelligence |
| **Response window** | < 45 min for initial cordon |
| **Force ratio** | Minimum 3:1 vs. estimated group |
| **Key constraint** | ROE graduated use of force; no cross-LoC without auth |

**Mission Workflow:**
1. Sensor Alert → BATMAN triggers Bayesian threat update
2. Force generation — available QRT / RR units identified from unit status DB
3. COA generation — cordon-and-search + blocking plan generated by HTN
4. War game — 500 MC runs; terrain, weather, night visibility factored
5. Commander approval — top-2 COAs presented with side-by-side risk comparison
6. Execution monitoring — position tracking, replanning triggers armed

**Simulation Variables:**
- Infiltrator group size: 3–15 (historical probability distribution)
- Detection probability: f(weather, vegetation density, sensor state)
- Escape probability: f(cordon speed, terrain, detection time lag)
- Civilian encounter probability: f(settlement proximity, time of day)

**AI Reasoning Chain:**
1. Bayesian update on group size from sensor RF/acoustic signature
2. GIS gradient analysis identifies optimal cordon geometry
3. RF propagation model places comms relay requirements
4. CBR retrieves structurally similar past cordons; seeds HTN

**Evaluation Metrics:**
- Time to cordon establishment
- Threat capture/neutralization rate
- Friendly casualties (expected vs. predicted)
- Civilian impact score
- ROE compliance score (% of simulation runs)

---

## 6.2 High-Altitude Logistics

| Attribute | Detail |
|---|---|
| **Altitude range** | 3,000–6,000m |
| **Modes** | Road, ALH Dhruv, porter/mule column, airdrop |
| **Key constraint** | ALH ceiling ~7,000m; winter road closures |
| **Critical unknowns** | Weather window, avalanche risk |

**Mission Workflow:**
1. Demand signal — forward post submits supply request
2. Route analysis — weather window, trafficability, interdiction probability
3. Mode selection — multi-modal optimization (road + air + porter mix)
4. Supply chain optimization — multi-stop routing with stockpile constraints
5. Risk assessment — avalanche risk per segment, weather confidence
6. Commander approval; dynamic monitoring with weather-triggered replan

**Simulation Variables:**
- Weather window: stochastic model (ECMWF-style distribution)
- Avalanche risk: slope × aspect × snowpack × historical frequency
- Vehicle trafficability: engine power degradation model at altitude
- Porter capacity: acclimatization state, load, altitude profile

**AI Reasoning:**
- Multi-modal optimizer minimizes: total_risk × time × resource_cost
- Stockpile forecasting: when does supply X reach critical threshold?
- Contingency plan: auto-generated if primary route is blocked

---

## 6.3 Counter-Terrorism (Urban)

| Attribute | Detail |
|---|---|
| **Time sensitivity** | High — hostage risk increases with delay |
| **Key constraint** | Minimize collateral damage; ROE lethal force threshold |
| **Intelligence base** | HUMINT + technical intelligence fusion |

**Mission Workflow:**
1. Intel fusion — building layout, entry points, threat/hostage disposition
2. Assault plan generation — multiple simultaneous breach options
3. Simulation — hostage safety probability distribution per option
4. Commander decision and approval

**Simulation Variables:**
- Hostage positions: probability distribution over floor plan
- Terrorist response: reactive vs. pre-planned (two agent behaviour modes)
- Structural characteristics: cover quality, entry vulnerability ratings
- Response force speed and breaching capability

---

## 6.4 Convoy Protection

**Planning Requirements:**
- IED probability heatmap per route segment (historical + intel)
- Escort vehicle formation optimization (doctrine template)
- Air cover coordination window
- MEDEVAC pre-positioning (satisfy response time ≤ 30 min anywhere on route)
- Alternative route pre-planning

**AI Reasoning:**
- IED probability = f(historical incidents, terrain type, route usage pattern, intel indicators)
- MEDEVAC placement solved as a coverage optimization problem (set-covering formulation)
- Formation spacing computed from IED blast radius model + vehicle separation doctrine

---

## 6.5 Disaster Relief (HADR)

| Attribute | Detail |
|---|---|
| **Difference from combat** | No threat agents; optimize lives saved, not threat elimination |
| **Extra actors** | NGOs, state government, NDRF — modelled as civilian logistics agents |

**Mission Workflow:**
1. Disaster assessment — affected area mapping (satellite / UAV data)
2. Demand estimation — affected population, supply requirements by type
3. Access analysis — blocked roads → alternate air/water routes identified
4. Resource allocation — engineering units, medical teams, rotary wing, boats
5. Distribution plan — supply drop zones, medical posts, evacuation corridors
6. Timeline optimization — prioritize most critical areas (triage-style)

**Key Simulation Metrics:** lives saved per hour, coverage radius, supply chain fill rate.

---

# 7. THREAT LIBRARY

## 7.1 Architecture

```
ThreatModel := {
  threat_id:         String,
  name:              String,
  category:          ThreatCategory,
  indicators:        [ThreatIndicator],    // observable signals
  behaviour_model:   AgentBehaviourSpec,   // for simulation
  planning_effects:  [PlanningEffect],     // how it changes COA
  risk_factors:      [RiskFactor],
  countermeasures:   [Countermeasure],
  historical_freq:   ProbabilityDistribution,
  seasonal_factors:  [SeasonalModifier]
}
```

## 7.2 Threat Catalogue

### T-01 — Cross-Border Infiltration

| Attribute | Value |
|---|---|
| Detection Signals | Sensor tripwire, UAV sighting, patrol contact, HUMINT |
| Planning Effect | Activate cordon-and-search template, aerial surveillance, alert adjacent units |
| Risk Score Formula | R = P(detection_failure) × P(escape) × group_size × threat_level |
| Simulation Variables | Group size [3–15], speed [2–8 km/h], route probability by terrain cover |
| Countermeasures | QRT deployment, aerial surveillance, cordon, tracker team |

---

### T-02 — UAV Reconnaissance

| Attribute | Value |
|---|---|
| Detection Signals | Radar contact, visual, RF frequency match, acoustic signature |
| Planning Effect | OPSEC degradation warning; recommend deception measures, position change |
| Risk Score Drivers | UAV type, loiter time over AOR, data relay capability |
| AI Response | Classify UAV from signature; estimate observed area; recommend counter-OPSEC |

---

### T-03 — Drone Swarm

| Attribute | Value |
|---|---|
| Detection Signals | RF cluster, multiple radar tracks, acoustic burst |
| Planning Effect | Activate counter-drone; restrict helicopter ops; disperse HVAs |
| Risk Score Drivers | Swarm size, payload type (unknown), coordination level |
| Simulation Variables | Trajectory model, kill probability per drone vs. SHORAD, saturation threshold |
| AI Response | Estimate counter-drone saturation point; recommend asset dispersal priority |

---

### T-04 — Loitering Munition

| Attribute | Value |
|---|---|
| Detection Signals | Slow radar contact, characteristic acoustic pattern, RF emission |
| Planning Effect | Route vehicles under overhead cover; disperse logistics; move HQ |
| Risk Score Drivers | Number of munitions, endurance, target discrimination capability |
| AI Response | Flag all exposed HVAs; recommend re-positioning under terrain/structure cover |

---

### T-05 — Electronic Warfare (EW / Jamming)

| Attribute | Value |
|---|---|
| Detection Signals | Comms degradation, GPS drift, BER increase, jammer DF fix |
| Planning Effect | Switch to EMCON plan; activate HF/satellite/courier comms; revise timing |
| Simulation Variables | Comms degradation model; command latency increase; navigation error accumulation |
| AI Response | Recommend frequency-hopping; pre-planned code words; estimate coordination latency |

---

### T-06 — GPS Degradation / Spoofing

| Attribute | Value |
|---|---|
| Detection Signals | GPS solution drift; receiver disagreement; anomalous fix confidence |
| Planning Effect | Switch to inertial + map-matching; reduce speed; pre-plan terrain checkpoints |
| AI Response | Identify GPS-dependent tasks; generate terrain checkpoint list; estimate timing degradation |

---

### T-07 — Cyber Incident (C2 / Comms)

| Attribute | Value |
|---|---|
| Detection Signals | Anomalous network traffic, auth failures, data integrity violations |
| Planning Effect | Isolate affected systems; downgrade to backup C2; restrict information sharing |
| AI Response | Identify backup command nodes; alternate comms tree; coordination degradation estimate |

---

### T-08 — IED Threat

| Attribute | Value |
|---|---|
| Detection Signals | HUMINT, pattern-of-life analysis, route usage pattern, engineer recon |
| Planning Effect | Route deviation; MRAP assignment; EOD pre-clearance requirement |
| Simulation Variables | IED trigger probability; vehicle survivability distribution; MEDEVAC response time |
| AI Response | IED probability heatmap per route segment; vehicle formation spacing; MEDEVAC pre-position |

---

### T-09 — Ambush Risk

| Attribute | Value |
|---|---|
| Detection Signals | Pattern-of-life deviation, choke point analysis, suspicious activity |
| Planning Effect | Avoid natural choke points; increase lead element standoff; pre-plan fire support |
| AI Response | Ambush suitability score per route segment; recommend alternatives; pre-plan quick reaction fire |

---

### T-10 — Extreme Weather

| Attribute | Value |
|---|---|
| Detection Signals | Weather forecast, sensor data, pilot / ground reports |
| Planning Effect | Suspend helicopter ops; reduce movement speed; extend timeline; pre-position shelter |
| AI Response | Weather-aware timeline revision; mission phase timing around weather windows |

---

### T-11 — Bridge Collapse / Road Denial

| Attribute | Value |
|---|---|
| Detection Signals | Engineering report, satellite imagery, patrol report |
| Planning Effect | Route replanning; bridging equipment requirement; timeline extension |
| AI Response | Trigger automatic route replan; check engineer asset availability; estimate timeline impact |

---

### T-12 — Hostage Situation

| Attribute | Value |
|---|---|
| Key Constraint | Maximise P(hostage_survival); minimise collateral damage |
| Simulation Variables | Hostage number, terrorist number, building geometry, response speed vs. hostage risk |
| AI Response | Simultaneous vs. sequential entry comparison; optimal breach points; distraction timing |

---

# 8. COA GENERATION ENGINE

## 8.1 Pipeline Architecture

```
COA GENERATION PIPELINE
═══════════════════════════════════════════════════════════════════
 MISSION INPUT
      │
      ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ MISSION DECOMPOSITION                                         │
 │  • Ontology lookup: mission_type → base template             │
 │  • Extract objectives, constraints, resources                 │
 │  • Build initial Task Network (HTN)                          │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ CBR RETRIEVAL                                                 │
 │  • Find K nearest past missions in FAISS index               │
 │  • Extract plan skeletons                                     │
 │  • Rank by adaptation cost                                   │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ PARALLEL COA GENERATION (3 concurrent threads)               │
 │                                                              │
 │  Thread A             Thread B             Thread C          │
 │  ─────────────        ──────────────       ──────────────    │
 │  "Bold"               "Balanced"           "Cautious"        │
 │  (aggressive          (doctrine-           (extended          │
 │   timeline,            optimal)             timeline,         │
 │   higher risk)                              reduced risk)     │
 │                                                              │
 │  Each thread: independent HTN planner                        │
 │  with different constraint weight vectors                    │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ CONSTRAINT VALIDATION                                         │
 │  • Hard constraint check (reject violating plans)            │
 │  • Resource feasibility check                                │
 │  • ROE compliance verification                               │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ WAR GAMING (per COA)                                         │
 │  • 500 Monte Carlo runs                                      │
 │  • Multi-agent simulation                                    │
 │  • Outcome distribution + failure mode analysis              │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ COA SCORING ENGINE                                           │
 │  • Multi-criteria utility function (commander-adjustable)    │
 │  • Risk-adjusted ranking                                     │
 │  • Explainability generation                                 │
 └──────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ COMMANDER REVIEW INTERFACE                                   │
 │  • Top-3 COAs with side-by-side comparison                  │
 │  • Full edit capability                                      │
 │  • Approval workflow                                         │
 └──────────────────────────────────────────────────────────────┘
═══════════════════════════════════════════════════════════════════
```

## 8.2 Path Planning (Hierarchical)

```
LEVEL 1 — Strategic Route Selection
  Algorithm:  Modified A* on road network graph
  Edge weight: composite(distance, threat_prob, trafficability, time)

LEVEL 2 — Operational Path Planning
  Algorithm:  Theta* (any-angle) on terrain raster
  Considers:  slope, vegetation, soil type, cover quality

LEVEL 3 — Tactical Final Approach
  Algorithm:  RRT* on micro-terrain / building geometry
  Considers:  cover & concealment, entry angles (urban)

PATH EDGE COST FUNCTION:
  cost(e) = w₁ × distance
           + w₂ × threat_probability
           + w₃ × exposure_time
           + w₄ × (1 − cover_factor)
           + w₅ × trafficability_penalty
           + w₆ × EW_risk

  Weights are mission-type specific and commander-tunable.
```

## 8.3 COA Utility Function

```
U(COA) = Σₖ [ wₖ × normalize(metricₖ(COA)) ]

METRIC                       DEFAULT WEIGHT   NOTE
─────────────────────────────────────────────────────────────────
P(mission_success)                0.35        from MC simulation
E[friendly_casualties]            0.25        lower is better
Time to objective                 0.15        faster if tactical
Resource efficiency               0.10        fuel, ammo
Risk concentration                0.08        avoid SPOF
P(ROE_compliance)                 0.04        from simulation
Flexibility / recoverability      0.03        ability to replan

RISK-ADJUSTED SCORE:
  U_adj(COA) = U(COA) × (1 − variance_penalty)
  variance_penalty = σ(outcome) / E(outcome)
  // High-uncertainty plans penalized even if mean is good

Commander adjusts weights interactively before generation.
BATMAN re-scores and re-ranks in real-time.
```

## 8.4 Commander Approval State Machine

```
APPROVAL WORKFLOW
══════════════════════════════════════════════════════════
[COAs Generated] ──▶ [Presented to Commander]
                              │
           ┌──────────────────┼───────────────────┐
           ▼                  ▼                   ▼
    [APPROVE as-is]   [MODIFY & APPROVE]    [REJECT ALL]
           │                  │                   │
           ▼                  ▼                   ▼
    [Log + Execute]   [Edit Interface]    [Re-specify mission]
                      [Re-validate]              │
                      [Re-simulate]              ▼
                      [Re-approve]        [Re-generate COAs]

All decisions logged with:
  • Commander identity (RBAC-verified)
  • Timestamp (tamper-evident)
  • What was changed (delta)
  • Reason (free-text field)
  • Cryptographic hash (audit chain)
══════════════════════════════════════════════════════════
```

---

# 9. WAR GAMING ENGINE — DIGITAL TWIN SIMULATION

## 9.1 Digital Twin Concept

```
BATMAN DIGITAL TWIN
══════════════════════════════════════════════════════════════
PHYSICAL WORLD                    DIGITAL TWIN
(Actual battlefield)              (BATMAN simulation)
───────────────────               ──────────────────────────
Terrain (physical)   ──sync──▶   Terrain Model (GIS / DEM)
Units (real)         ──sync──▶   Entity Agents
Weather (actual)     ──sync──▶   Stochastic Weather Model
Infrastructure       ──sync──▶   Infrastructure Graph
Sensor network       ──sync──▶   Sensor Coverage Model

[BATMAN v1: physical world data is simulated / manually imported]
[Production: real-time feeds update the twin continuously]
══════════════════════════════════════════════════════════════
```

## 9.2 Simulation Core (Discrete Event)

```python
class BATMANSimulation:
    """
    Discrete Event Simulation engine with continuous terrain physics.
    """
    components = {
        "event_queue":    PriorityQueue,   # future events
        "entity_pool":    AgentPool,       # all simulated agents
        "terrain_model":  GISTerrain,      # raster physics
        "weather_model":  StochasticWx,    # weather evolution
        "comms_model":    RFPropagation,   # link quality
        "sensor_model":   DetectionSurf,   # P(detect) surfaces
        "logistics_model": ConsumptionTrk, # fuel/ammo tracking
        "judge_model":    OutcomeEval,     # ROE + objective scoring
    }

    def run(self):
        while not self.termination_condition():
            event = self.event_queue.pop_earliest()
            handler = self.dispatch_table[event.type]
            new_events = handler.process(event, self.world_state)
            self.event_queue.push_all(new_events)
            self.world_state.update(event)
            self.judge_model.evaluate(self.world_state)
        return SimulationOutcome(self.world_state, self.event_log)
```

## 9.3 Terrain Physics Model

```
TERRAIN PHYSICS MODEL
════════════════════════════════════════════════════════════
Input data sources:
  • DEM: SRTM 30m / Cartosat-DEM (India)
  • Vegetation: ESA WorldCover
  • Soil: ISRO soil type raster
  • Roads: OSM + military road network

Derived layers (computed at load time):
  • Slope gradient map (from DEM, Sobel filter)
  • Trafficability map: f(slope, soil, vegetation)
    − Vehicle-type dependent (wheeled vs. tracked)
  • Line-of-sight (LOS): pre-computed intervisibility grid
  • RF propagation: obstacle height profile per link
  • Cover & concealment: vegetation density × LOS inverse
  • Flood susceptibility: DEM watershed + precipitation model
  • Avalanche risk: slope + aspect + historical frequency

Movement speed model:
  speed(entity, terrain) =
    base_speed(entity_type)
    × trafficability_factor(terrain)
    × slope_factor(gradient)
    × weather_factor(current_wx)
    × load_factor(payload)
    × lighting_factor(time_of_day)
════════════════════════════════════════════════════════════
```

## 9.4 Monte Carlo Engine

```
MONTE CARLO SIMULATION PROTOCOL
═══════════════════════════════════════════════════════════════
For each COA:

1. SAMPLE — Draw N=500 samples from uncertainty distributions:
   • Threat behaviour     (from threat agent models)
   • Detection probabilities (from sensor model)
   • Weather realisation  (from stochastic weather model)
   • Comms reliability    (RF model + EW threat)
   • Civilian encounter   (from population density map)

2. SIMULATE — Run full DES for each sample in parallel
   (multiprocessing pool, 16 workers target)

3. AGGREGATE — Compute over N outcomes:
   • P(mission_success)   = count(success) / N
   • E[casualties]        = mean(casualties_per_run)
   • σ(casualties)        = std(casualties_per_run)
   • P(ROE_violation)     = count(roe_event) / N
   • Timeline quantiles:  [P5, P50, P95]

4. SENSITIVITY ANALYSIS
   • Sobol indices — identify variables driving outcome variance
   • Report: "Mission success most sensitive to [variable X]"

5. FAILURE MODE ANALYSIS
   • Top-5 failure modes by frequency across runs
   • Presented as prioritized risk factors in explanation

COMPUTATIONAL BUDGET:
  500 runs × 3 COAs = 1,500 simulations
  Target: complete in < 90 seconds on server hardware
  Via: multiprocessing, simplified physics, cached terrain
═══════════════════════════════════════════════════════════════
```

## 9.5 After Action Review (AAR) Engine

```
AAR CAPABILITIES
══════════════════════════════════════════════════════════
1. TIMELINE RECONSTRUCTION
   • Full event log replay at any speed (0.1×–100×)
   • Pause, step forward/back at any event
   • Counterfactual: "What if COA-1 had been chosen?"

2. DECISION AUDIT
   • Every commander decision shown with context
   • AI recommendation vs. actual decision
   • Actual outcome vs. predicted distribution

3. PERFORMANCE ANALYSIS
   • Calibration: were confidence scores accurate?
   • Prediction error identification → model improvement

4. LEARNING EXTRACTION
   • Novel tactics flagged (not in template library)
   • Suggested doctrine update items
   • New case added to mission memory

5. REPORT GENERATION
   • Structured AAR in Indian Army format
   • Mission timeline visualization export
   • Lessons-learned section (structured + free-text)
══════════════════════════════════════════════════════════
```

---

# 10. HUMAN-IN-THE-LOOP FRAMEWORK

## 10.1 Four HITL Guarantees

1. **No autonomous action** — BATMAN cannot execute any action without explicit commander authorization
2. **Full transparency** — Every AI recommendation includes its reasoning chain
3. **Complete override** — Commander can modify any AI output at any granularity
4. **Full auditability** — Every decision, override, and rationale is logged immutably

## 10.2 Interaction Modes

```
INTERACTION SPECTRUM
══════════════════════════════════════════════════════════════
AI-HEAVY ◄────────────────────────────────────────► AI-MINIMAL

MODE 1 — PLANNING ASSIST
  AI generates full COAs; commander reviews and approves.
  Use: Time-available planning sessions.

MODE 2 — INTERACTIVE PLANNING
  Commander drives; AI provides real-time constraint feedback,
  risk assessment, and suggestions as the plan is built.
  Use: Complex, novel, unprecedented situations.

MODE 3 — MONITORING + ADVISORY
  Mission in execution; AI monitors and alerts.
  Commander queries AI for specific point assessments.
  Use: Execution phase.

MODE 4 — EMERGENCY REPLAN
  Trigger event detected; AI generates rapid contingency
  plan, presents with visual urgency indicator.
  Use: Dynamic situation changes during execution.
══════════════════════════════════════════════════════════════
```

## 10.3 What-If Analysis

Commander modifies any parameter → immediately sees:

```
WHAT-IF QUERIES (examples):

"What if one helicopter becomes unserviceable?"
  → Re-runs resource allocation sans that asset
  → Shows which tasks are no longer feasible
  → Proposes workaround options

"What if we delay H-Hour by 2 hours?"
  → Re-evaluates all time-dependent constraints
  → Shows weather window impact, threat window shift

"What if the northern route is compromised?"
  → Replans with northern route blocked in GIS
  → Shows alternative routes with risk delta
  → Re-simulates and updates COA ranking
```

## 10.4 Role-Based Access Control

| Role | View | What-If | Edit | Approve | Admin |
|---|---|---|---|---|---|
| Commanding Officer | ✓ | ✓ | ✓ | ✓ | — |
| 2IC / Ops Officer | ✓ | ✓ | ✓ | COAs | — |
| Intelligence Officer | ✓ | Intel | Intel | — | — |
| Logistics Officer | ✓ | Logs | Logs | — | — |
| BATMAN Operator | ✓ | ✓ | — | — | ✓ |

## 10.5 Confidence Visualization

```
CONFIDENCE INDICATOR SYSTEM

  ██████████ HIGH   (>85%)  — Solid colour, no qualifier
  ████████░░ MEDIUM (60–85%)— Slight desaturation + "est." label
  ████░░░░░░ LOW    (30–60%)— Hatching + explicit [LOW CONF] badge
  ██░░░░░░░░ VERY LOW (<30%)— Red border + ⚠ warning tooltip

Example display:
  Risk Score: 7.2 / 10  [Confidence: 74% — MEDIUM]
  │
  └─ "This score is based on limited intelligence.
      Key unknown: exact infiltrator group size."
```

---

# 11. COMMAND DASHBOARD

## 11.1 Screen 1 — Main Command View

```
╔════════════════════════════════════════════════════════════════════╗
║  BATMAN v2.0  │  MISSION: COUNTER-INFILTRATION — KARGIL SECTOR     ║
║  [UNCLASSIFIED — DEMO]           14 AUG 2026  17:45 IST  ● LIVE   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  ┌──────────────────────────────────┐  ┌────────────────────────┐ ║
║  │                                  │  │  SITUATION SUMMARY     │ ║
║  │       ANIMATED 3D GIS MAP        │  │                        │ ║
║  │                                  │  │ THREAT LEVEL: ▐▐▐▐HIGH │ ║
║  │  • Terrain: shaded relief        │  │ ██████████░ 87%        │ ║
║  │  • Own forces: blue icons        │  │                        │ ║
║  │  • Threat: red probability heat  │  │ ACTIVE UNITS:    12    │ ║
║  │  • Cordon: yellow overlay        │  │ OPERATIONAL:     11    │ ║
║  │  • Routes: animated arrows       │  │                        │ ║
║  │  • Weather: cloud/wind overlay   │  │ ACTIVE THREATS:   2    │ ║
║  │                                  │  │ Infiltration  P=0.83   │ ║
║  │  [PAN][ZOOM][MEASURE][DRAW]      │  │ UAV sighting  P=0.67   │ ║
║  │  [TERRAIN][THREAT][UNITS][WX]    │  │                        │ ║
║  └──────────────────────────────────┘  │ MISSION PHASE: 2 of 4  │ ║
║                                        │ H+02:47 ████████░░░░   │ ║
║                                        └────────────────────────┘ ║
║  ┌──────────────────┐  ┌──────────────┐  ┌─────────────────────┐ ║
║  │  COA STATUS      │  │  RISK RADAR  │  │  ALERTS             │ ║
║  │                  │  │              │  │                     │ ║
║  │  ✓ COA-2 Active  │  │  [Radial     │  │ ⚠ Comms degraded   │ ║
║  │  H+0:45 to Obj.  │  │   chart:     │  │   Sector-3  [12m]  │ ║
║  │                  │  │   terrain,   │  │                     │ ║
║  │  Next decision:  │  │   threat,    │  │ ✓ ALPHA: OBJ reached│ ║
║  │  Phase 3 at H+1  │  │   logistics, │  │   [08m]            │ ║
║  │                  │  │   comms,     │  │                     │ ║
║  │  [OVERRIDE]      │  │   weather]   │  │ ℹ Weather update    │ ║
║  │  [EMERGENCY RPL] │  │              │  │   in 30 min [now]   │ ║
║  └──────────────────┘  └──────────────┘  └─────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝
```

## 11.2 Screen 2 — COA Comparison

```
╔════════════════════════════════════════════════════════════════════╗
║  COA COMPARISON  │  MISSION: CI-KARGIL-2026-0814                   ║
╠════════════════════════════════════════════════════════════════════╣
║  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐  ║
║  │     COA - 1      │ │     COA - 2      │ │     COA - 3      │  ║
║  │   "Bold Cordon"  │ │  "Phased Block"  │ │  "Aerial First"  │  ║
║  │                  │ │  ★ RECOMMENDED   │ │                  │  ║
║  ├──────────────────┤ ├──────────────────┤ ├──────────────────┤  ║
║  │ SUCCESS:   71%   │ │ SUCCESS:   84%   │ │ SUCCESS:   67%   │  ║
║  │ CAS: 1.8 (σ=1.1) │ │ CAS: 0.9 (σ=0.7)│ │ CAS: 2.1 (σ=1.4)│  ║
║  │ TIME:      2.5h  │ │ TIME:      3.2h  │ │ TIME:      2.0h  │  ║
║  │ RISK:      HIGH  │ │ RISK:    MEDIUM  │ │ RISK:      HIGH  │  ║
║  │ FUEL:       85%  │ │ FUEL:       72%  │ │ FUEL:       90%  │  ║
║  ├──────────────────┤ ├──────────────────┤ ├──────────────────┤  ║
║  │ TOP RISK:        │ │ TOP RISK:        │ │ TOP RISK:        │  ║
║  │ N-flank escape   │ │ Timing delay     │ │ Weather window   │  ║
║  │ P = 0.31         │ │ P = 0.18         │ │ P = 0.39         │  ║
║  ├──────────────────┤ ├──────────────────┤ ├──────────────────┤  ║
║  │ [SIMULATE] [SEL] │ │ [SIMULATE] [SEL★]│ │ [SIMULATE] [SEL] │  ║
║  │ [MODIFY]         │ │ [MODIFY]         │ │ [MODIFY]         │  ║
║  └──────────────────┘ └──────────────────┘ └──────────────────┘  ║
║                                                                    ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  AI REASONING — Why COA-2 is recommended                     │ ║
║  │                                                               │ ║
║  │  PRIMARY:    Highest success probability (84%) / 500 runs    │ ║
║  │  SECONDARY:  Lowest expected casualties (0.9, σ=0.7)         │ ║
║  │  TRADE-OFF:  42 min longer than COA-1                        │ ║
║  │  KEY RISK:   Timing delay if QRT > 15 min late (P=0.18)     │ ║
║  │  PRECEDENT:  Similar to CI-BARAMULLA-2024 [SUCCESS]          │ ║
║  │                                                               │ ║
║  │  [EXPAND REASONING]  [SHOW SIMULATION]  [ADJUST WEIGHTS]     │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝
```

## 11.3 Screen 3 — War Game Playback

```
╔════════════════════════════════════════════════════════════════════╗
║  WAR GAME  │  COA-2 "Phased Block"  │  Run 1 of 500              ║
╠════════════════════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │            ANIMATED MAP (entity icons on terrain)            │ ║
║  │   [Event markers: contact ✕, alert ⚠, task complete ✓]      │ ║
║  │   [Probability haze updates as simulation progresses]        │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
║  TIMELINE:  ├──H──────────────────────────────────────────┤       ║
║             0:00   0:30   1:00   1:30   2:00   2:30   3:00        ║
║             ●Deploy ●OPs  ▶HERE  ●OBJ   ●Exfil          ●End     ║
║                                                                    ║
║  [◀◀ REWIND] [◀STEP] [▶PLAY] [▶▶ FAST] [⏸ PAUSE] [SPEED: 5×]   ║
║  [ALL RUNS HEATMAP]  [WORST CASE]  [BEST CASE]  [MEDIAN]         ║
║                                                                    ║
║  EVENT LOG (this run)                                              ║
║  ──────────────────────────────────────────────────────           ║
║  H+0:47  ALPHA: contact Grid 4378 — 3 persons                     ║
║  H+0:52  Bayesian update: P(group≥5) → 0.71                      ║
║  H+0:58  BRAVO: blocking pos NORTH — ✓ reached                    ║
║  H+1:04  ⚠ Comms degraded ALPHA↔HQ — relay auto-activated        ║
║  H+1:22  Contact contained — CHARLIE closing — ROE: YELLOW        ║
╚════════════════════════════════════════════════════════════════════╝
```

## 11.4 Screen 4 — Logistics Dashboard

```
╔════════════════════════════════════════════════════════════════════╗
║  LOGISTICS STATUS  │  CI-KARGIL-2026-0814                         ║
╠════════════════════════════════════════════════════════════════════╣
║  FUEL:                                                             ║
║  ALPHA  ████████░░ 82%    BRAVO  ██████░░░░ 64%                   ║
║  CHARLIE███████████ 91%   DELTA  ████░░░░░░ 41% ⚠ CRITICAL        ║
║  FORECAST: DELTA reaches 20% at H+2:15                            ║
║  → AI: Pre-position fuel at Grid 4412 by H+1:45                   ║
║  ────────────────────────────────────────────────────────         ║
║  AMMUNITION:                                                       ║
║  INSAS 5.56 ██████████ 91% (12,400 rds)                          ║
║  UBGL       ███████░░░ 68% (34 rnds)                              ║
║  ────────────────────────────────────────────────────────         ║
║  MEDICAL ASSETS:                                                   ║
║  ◉ MRT ALPHA: Grid 4302  Radius: 8.4 km   ✓ OK                   ║
║  ◉ MRT BRAVO: Grid 4589  Radius: 6.1 km   ✓ OK                   ║
║  ▲ COVERAGE GAP: eastern sector — 12 km uncovered                 ║
║  → AI: Reposition MRT BRAVO to Grid 4480 to close gap            ║
║  ────────────────────────────────────────────────────────         ║
║  SUPPLY LINES:                                                     ║
║  Route A (primary):  ████████░░ CLEAR        80% confidence       ║
║  Route B (alt):      ██░░░░░░░░ HIGH RISK    IED P=0.34           ║
╚════════════════════════════════════════════════════════════════════╝
```

## 11.5 Screen 5 — Knowledge Graph Visualization

```
╔════════════════════════════════════════════════════════════════════╗
║  KNOWLEDGE GRAPH  │  Current Battlefield State                     ║
╠════════════════════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │  [Force-directed graph layout — interactive]                  │ ║
║  │                                                              │ ║
║  │  (Alpha Unit) ──[assigned_to]──▶ (Obj: North Cordon)        │ ║
║  │       │                                  ▲                  │ ║
║  │   [commands]                          [threatens]           │ ║
║  │       │                                  │                  │ ║
║  │  (Delta Section) ──[positions]──▶ (Grid 4378) ◄─ (Threat)  │ ║
║  │                                       │                     │ ║
║  │                               [adjacent_to]                 │ ║
║  │                                       │                     │ ║
║  │                               (Ridge Line)                  │ ║
║  │                                                              │ ║
║  │  Click any node: expand neighbours                           │ ║
║  │  Filter: [UNITS] [THREATS] [TERRAIN] [OBJECTIVES] [ROUTES]  │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
╚════════════════════════════════════════════════════════════════════╝
```

---

# 12. AI LEARNING & CONTINUOUS IMPROVEMENT

## 12.1 Learning Sources

```
BATMAN LEARNING ECOSYSTEM
══════════════════════════════════════════════════════════════════
SOURCE 1 — War Gaming Simulation (Primary)
  • Nightly batch: 10,000 simulation runs
  • Varied across: threat scenarios, weather, force composition
  • Output: labelled (plan → outcome) training pairs

SOURCE 2 — Actual Mission Outcomes (Secondary)
  • Post-mission AAR data entry (structured)
  • Calibration: actual vs. predicted distribution
  • Delta feeds model improvement

SOURCE 3 — Commander Feedback (Tertiary)
  • Override actions (AI chose X; commander chose Y)
  • What-if queries (reveals priority weighting)
  • Manual plan edits (reveals unsatisfied constraints)
══════════════════════════════════════════════════════════════════
```

## 12.2 Offline Training Pipeline

```
NIGHTLY TRAINING CYCLE
═══════════════════════════════════════════════════════════════════
1. DATA COLLECTION
   simulation_runner.run_batch(N=10_000, all_mission_types)
   feature_extractor.process(logs) → training_dataset.parquet

2. MODEL TRAINING
   a. GNN (Battlefield Reasoning Network):
      trainer.train(BRN, training_dataset, epochs=50)
      → Updated outcome prediction model

   b. HTN Heuristic Weights:
      heuristic_learner.update(success_cases, failure_cases)
      → Updated method ranking heuristics

   c. CBR Similarity Weights:
      cbr_trainer.optimise(retrieval_quality_feedback)
      → Updated similarity metric

3. EVALUATION
   validator.evaluate(new_model, held_out_test_set)
   Checks: accuracy, calibration, regression vs. old model

4. VERSIONING & DEPLOYMENT
   if validator.passes_threshold():
       registry.deploy(new_model, version=bump())
   else:
       registry.flag_for_review(new_model)

5. DRIFT MONITORING (rolling 30-day window)
   if monitor.detects_drift(prediction_vs_outcome):
       trigger_retraining()
═══════════════════════════════════════════════════════════════════
```

## 12.3 Mission Memory Schema

```
MissionCase := {
  case_id:     UUID,
  created_at:  Timestamp,

  // Retrieval features
  mission_type:     MissionType,
  aor_embedding:    Vector[128],    // terrain signature (compressed)
  threat_profile:   Vector[32],     // threat type encoding
  resource_profile: Vector[16],     // force composition
  timeline_params:  TemporalParams,
  season:           Season,

  // Plan
  coa_selected:   COASnapshot,
  modifications:  [CommanderEdit],  // what commander changed

  // Outcome labels
  outcome:          MissionOutcome,
  actual_metrics:   {casualties, time, fuel_used, ...},
  predicted_metrics:{from_simulation},
  prediction_error: Float,

  // Learning annotations
  lessons_learned:  [String],
  failure_modes:    [FailureMode],
  novel_tactics:    [TacticDescription]
}
```

---

# 13. TECHNOLOGY STACK

```
BATMAN TECHNOLOGY STACK — PRODUCTION QUALITY
══════════════════════════════════════════════════════════════════════
LAYER           TECHNOLOGY              JUSTIFICATION
────────────────────────────────────────────────────────────────────
FRONTEND        React 18 + TypeScript   Component reuse, type safety
                Vite                    Fast dev + prod builds
                MapLibre GL + Leaflet   Open-source GIS, offline tiles
                D3.js                   Custom force-directed KG viz
                Three.js                3D terrain (future twin)
                Apache ECharts          Charts, radar, timeline
                Redux Toolkit           Predictable state management
────────────────────────────────────────────────────────────────────
BACKEND         Python 3.12             AI ecosystem compatibility
                FastAPI                 Async, OpenAPI, high perf
                Celery + Redis          Async simulation queue
                Apache Kafka            Event streaming / C2 bus
────────────────────────────────────────────────────────────────────
AI ENGINE       Custom HTN Planner      Domain-specific, auditable
                PyKE / CLIPS            RETE rule engine
                pgmpy                   Bayesian network inference
                PyTorch Geometric       GNN (GraphSAGE / GAT)
                scikit-learn            Classical ML scoring models
                DEAP                    ACO / genetic optimizer
                SimPy                   Discrete event simulation
                Mesa                    Multi-agent simulation
                FAISS                   CBR vector similarity search
────────────────────────────────────────────────────────────────────
GIS             PostGIS 3.4             Spatial SQL + index support
                GeoServer               WMS / WFS tile serving
                GDAL / Rasterio         DEM raster analysis
                Shapely + GeoPandas     Geometry computation
                OpenDEM (SRTM)          Terrain elevation data
────────────────────────────────────────────────────────────────────
GRAPH DB        Neo4j 5.x               Native graph (Cypher queries)
                Apache Jena (OWL 2)     Ontology reasoning
────────────────────────────────────────────────────────────────────
DATABASES       PostgreSQL 16 + PostGIS Primary relational + spatial
                MongoDB 7               Mission memory (documents)
                InfluxDB 2.x            Time series (sensor data)
                Redis 7                 Cache + Celery broker
────────────────────────────────────────────────────────────────────
SEARCH          Apache Solr / FAISS     CBR case retrieval indexing
────────────────────────────────────────────────────────────────────
CONTAINERS      Docker + Compose        Dev / test environment
                Kubernetes              Production orchestration
                Helm                    K8s package management
────────────────────────────────────────────────────────────────────
SECURITY        Keycloak                OIDC + RBAC identity
                HashiCorp Vault         Secrets management
                TLS 1.3 everywhere      In-transit encryption
                AES-256-GCM             At-rest encryption
                Immutable audit chain   Tamper-evident decisions
────────────────────────────────────────────────────────────────────
MONITORING      Prometheus + Grafana    System observability
                OpenTelemetry           Distributed tracing
                ELK Stack               Centralized logging
────────────────────────────────────────────────────────────────────
DEPLOYMENT      Air-gapped on-premise   Classified environment
                Edge compute nodes      Forward-deployed COPs
                Offline-capable PWA     Tactical terminal use
══════════════════════════════════════════════════════════════════════
```

---

# 14. SOFTWARE ARCHITECTURE

## 14.1 Microservice Map

```
SERVICE                  PORT   RESPONSIBILITY
───────────────────────────────────────────────────────────────────
batman-gateway           8080   API gateway, auth, rate limiting
batman-mission-svc       8001   Mission CRUD, lifecycle management
batman-planning-svc      8002   HTN planner, COA generation
batman-wargame-svc       8003   Simulation engine, MC orchestrator
batman-threat-svc        8004   Threat library, risk assessment
batman-logistics-svc     8005   Resource tracking, allocation
batman-kg-svc            8006   Knowledge graph queries (Neo4j)
batman-gis-svc           8007   Spatial queries, terrain analysis
batman-sa-svc            8008   Situation awareness fusion
batman-aar-svc           8009   After action review, replay engine
batman-learn-svc         8010   Offline training pipeline
batman-audit-svc         8011   Immutable decision audit log
batman-notify-svc        8012   Alert routing, notifications
batman-ui                3000   React frontend (PWA)
───────────────────────────────────────────────────────────────────
INFRASTRUCTURE:
kafka-broker             9092   Mission command event bus
redis-cache              6379   Cache + Celery broker
neo4j-graph              7474   Knowledge graph
postgres-primary         5432   Primary relational DB
mongodb-memory           27017  Mission memory store
influxdb-ts              8086   Time series data
geoserver                8090   Map tile serving
keycloak-iam             8443   Identity & access management
vault-secrets            8200   Secrets management
```

## 14.2 Folder Structure

```
batman/
├── frontend/                     # React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── map/              # GIS components (MapLibre)
│   │   │   ├── coa/              # COA comparison, approval UI
│   │   │   ├── simulation/       # Wargame playback
│   │   │   ├── logistics/        # Logistics dashboard
│   │   │   ├── kg/               # Knowledge graph visualization
│   │   │   └── shared/           # Common components
│   │   ├── pages/
│   │   ├── store/                # Redux Toolkit slices
│   │   ├── services/             # API + WebSocket clients
│   │   └── utils/
│   └── public/
│
├── services/                     # Backend microservices
│   ├── gateway/                  # FastAPI API gateway
│   ├── mission-svc/
│   ├── planning-svc/
│   │   ├── htn/                  # HTN planner core
│   │   ├── cbr/                  # Case-based reasoning
│   │   ├── constraint/           # ACO constraint solver
│   │   └── coa/                  # COA generator
│   ├── wargame-svc/
│   │   ├── simulation/           # SimPy DES engine
│   │   ├── agents/               # Agent definitions (Mesa)
│   │   ├── terrain/              # Terrain physics
│   │   └── monte_carlo/          # MC orchestrator
│   ├── threat-svc/
│   │   ├── bayesian/             # Bayesian network (pgmpy)
│   │   ├── threat_library/       # Threat model definitions
│   │   └── risk_scorer/
│   ├── kg-svc/                   # Neo4j + OWL ontology
│   ├── gis-svc/                  # PostGIS + GDAL analysis
│   ├── logistics-svc/
│   ├── sa-svc/                   # Situation awareness fusion
│   ├── learn-svc/                # Training pipeline
│   ├── aar-svc/                  # After action review
│   └── audit-svc/                # Immutable audit chain
│
├── ai/                           # Shared AI modules
│   ├── models/                   # Trained model artefacts
│   │   ├── gnn/
│   │   ├── heuristics/
│   │   └── registry.yaml         # Version registry
│   ├── training/                 # Training scripts
│   ├── evaluation/               # Evaluation harness
│   └── ontology/                 # OWL 2 ontology files
│
├── data/
│   ├── terrain/                  # DEM, terrain tiles (India)
│   ├── threat_library/           # Threat model JSON/YAML
│   ├── doctrine/                 # Doctrinal templates (YAML)
│   ├── mission_memory/           # CBR seed cases (200+)
│   └── seeds/                    # DB seed scripts
│
├── infra/
│   ├── docker/
│   ├── k8s/
│   ├── helm/
│   └── terraform/
│
└── tests/
    ├── unit/
    ├── integration/
    ├── simulation_validation/
    └── security/
```

---

# 15. DATABASE DESIGN

## 15.1 PostgreSQL + PostGIS Schema

```sql
-- ── ENUMS ────────────────────────────────────────────────────────
CREATE TYPE mission_type_enum AS ENUM (
  'COUNTER_INFILTRATION','COUNTER_TERRORISM','COUNTER_INSURGENCY',
  'CONVOY_PROTECTION','HIGH_ALTITUDE_LOGISTICS','HADR',
  'HOSTAGE_RESCUE','BORDER_SURVEILLANCE','CRITICAL_INFRA_SECURITY'
);
CREATE TYPE mission_status_enum AS ENUM (
  'PLANNING','APPROVED','EXECUTING','COMPLETE','ABORTED'
);
CREATE TYPE readiness_enum AS ENUM ('GREEN','AMBER','RED','BLACK');
CREATE TYPE coa_status_enum AS ENUM (
  'DRAFT','SIMULATED','PRESENTED','APPROVED','REJECTED','EXECUTED'
);
CREATE TYPE audit_event_enum AS ENUM (
  'COA_PRESENTED','COA_APPROVED','COA_REJECTED','COA_MODIFIED',
  'PLAN_OVERRIDE','REPLAN_TRIGGERED','MISSION_STARTED',
  'MISSION_COMPLETED'
);

-- ── MISSIONS ─────────────────────────────────────────────────────
CREATE TABLE missions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_code    VARCHAR(50) UNIQUE NOT NULL,
  mission_type    mission_type_enum NOT NULL,
  status          mission_status_enum NOT NULL DEFAULT 'PLANNING',
  classification  VARCHAR(20) NOT NULL,
  created_by      UUID REFERENCES users(id),
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  aor             GEOMETRY(POLYGON, 4326),  -- Area of Responsibility
  h_hour          TIMESTAMPTZ,
  mission_params  JSONB NOT NULL DEFAULT '{}',
  constraint_ids  UUID[]
);

-- ── OBJECTIVES ───────────────────────────────────────────────────
CREATE TABLE objectives (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id      UUID REFERENCES missions(id) ON DELETE CASCADE,
  obj_type        VARCHAR(50) NOT NULL,
  priority        INTEGER CHECK (priority BETWEEN 1 AND 5),
  target_location GEOMETRY(POINT, 4326),
  deadline        TIMESTAMPTZ,
  status          VARCHAR(20) DEFAULT 'PENDING',
  description     TEXT
);

-- ── COURSES OF ACTION ────────────────────────────────────────────
CREATE TABLE courses_of_action (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id      UUID REFERENCES missions(id) ON DELETE CASCADE,
  coa_number      INTEGER,
  name            VARCHAR(100),
  style           VARCHAR(20),    -- BOLD | BALANCED | CAUTIOUS
  status          coa_status_enum DEFAULT 'DRAFT',
  plan_graph      JSONB,          -- HTN plan as JSON graph
  resource_plan   JSONB,
  timeline        JSONB,
  utility_score   FLOAT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── SIMULATION RESULTS ───────────────────────────────────────────
CREATE TABLE simulation_results (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  coa_id          UUID REFERENCES courses_of_action(id),
  run_count       INTEGER NOT NULL,
  success_rate    FLOAT,
  mean_casualties FLOAT,
  std_casualties  FLOAT,
  timeline_p50    INTERVAL,
  timeline_p95    INTERVAL,
  roe_violation_rate FLOAT,
  failure_modes   JSONB,          -- [{mode, probability}, ...]
  sensitivity     JSONB,          -- Sobol indices
  computed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── THREAT ASSESSMENTS ───────────────────────────────────────────
CREATE TABLE threat_assessments (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id      UUID REFERENCES missions(id),
  threat_type     VARCHAR(50) NOT NULL,
  probability     FLOAT CHECK (probability BETWEEN 0 AND 1),
  confidence      FLOAT CHECK (confidence BETWEEN 0 AND 1),
  risk_score      FLOAT,
  location        GEOMETRY(POINT, 4326),
  uncertainty_m   FLOAT,          -- uncertainty radius in metres
  evidence        JSONB,
  bayesian_params JSONB,          -- prior, likelihood, posterior
  assessed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- ── UNITS ────────────────────────────────────────────────────────
CREATE TABLE units (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  unit_code        VARCHAR(50) UNIQUE NOT NULL,
  unit_type        VARCHAR(50) NOT NULL,
  parent_unit_id   UUID REFERENCES units(id),
  current_position GEOMETRY(POINT, 4326),
  status           readiness_enum DEFAULT 'GREEN',
  capabilities     TEXT[],
  fuel_level       FLOAT CHECK (fuel_level BETWEEN 0 AND 1),
  ammo_state       JSONB,
  personnel_count  INTEGER,
  comms_status     VARCHAR(20),
  last_updated     TIMESTAMPTZ DEFAULT NOW()
);

-- ── DECISION AUDIT (append-only, immutable) ──────────────────────
CREATE TABLE decision_audit (
  id                BIGSERIAL PRIMARY KEY,
  event_type        audit_event_enum NOT NULL,
  mission_id        UUID,
  coa_id            UUID,
  actor_id          UUID REFERENCES users(id),
  actor_role        VARCHAR(50),
  timestamp         TIMESTAMPTZ DEFAULT NOW(),
  ai_recommendation JSONB,
  human_decision    JSONB,
  rationale         TEXT,
  session_id        UUID,
  checksum          BYTEA     -- SHA-256(prev_checksum || row_data)
);
-- No UPDATE or DELETE granted on decision_audit to ANY role.
-- Enforced via row-level security policy.

-- ── SPATIAL INDEXES ──────────────────────────────────────────────
CREATE INDEX idx_units_position     ON units USING GIST(current_position);
CREATE INDEX idx_missions_aor       ON missions USING GIST(aor);
CREATE INDEX idx_threats_location   ON threat_assessments USING GIST(location);
CREATE INDEX idx_objectives_loc     ON objectives USING GIST(target_location);
```

---

# 16. DEVELOPMENT ROADMAP

## 16.1 REST + WebSocket API

```
BASE URL: https://batman-gw.mil.internal/api/v1
AUTH:     Bearer JWT (Keycloak)  — all endpoints require authentication

── MISSION ──────────────────────────────────────────────────────────
POST   /missions                      Create mission
GET    /missions/{id}                 Get mission detail
PUT    /missions/{id}                 Update mission parameters
GET    /missions/{id}/status          Live mission status

── COA ──────────────────────────────────────────────────────────────
POST   /missions/{id}/coa/generate    Trigger COA generation (async)
                                      Body: {weights, constraint_overrides}
                                      Returns: {job_id}
GET    /jobs/{job_id}                 Poll job status
GET    /missions/{id}/coa             List all COAs
GET    /missions/{id}/coa/{coa_id}    COA detail + explanation object
PUT    /missions/{id}/coa/{coa_id}    Modify COA (commander edit)
POST   /missions/{id}/coa/{coa_id}/approve    Approve COA
POST   /missions/{id}/coa/{coa_id}/reject     Reject COA + reason

── SIMULATION ───────────────────────────────────────────────────────
POST   /missions/{id}/coa/{coa_id}/simulate   Run war game
GET    /simulations/{sim_id}                   Results + statistics
GET    /simulations/{sim_id}/replay            Replay event stream
POST   /missions/{id}/whatif                   What-if analysis
                                               Body: {parameter_overrides}

── THREAT ───────────────────────────────────────────────────────────
GET    /threats                       All active threat models
POST   /missions/{id}/threats/assess  Trigger Bayesian assessment
GET    /missions/{id}/threats         Mission threat assessment

── GIS ──────────────────────────────────────────────────────────────
GET    /gis/terrain/{bbox}            Terrain data (DEM, cover)
GET    /gis/route                     Route planning (A* / Theta*)
                                      Query: from, to, mode, mission_id
GET    /gis/los                       Line-of-sight analysis
POST   /gis/analyse                   Terrain analysis polygon

── KNOWLEDGE GRAPH ──────────────────────────────────────────────────
GET    /kg/entity/{id}                Entity + neighbours
GET    /kg/reasoning/{mission_id}     GNN reasoning output
POST   /kg/query                      Read-only Cypher query

── AUDIT ────────────────────────────────────────────────────────────
GET    /audit/decisions/{mission_id}  Full decision audit trail
GET    /audit/verify/{entry_id}       Verify checksum integrity

── WEBSOCKET CHANNELS ───────────────────────────────────────────────
ws://.../ws/mission/{id}/live         Live situation updates (push)
ws://.../ws/simulation/{id}/play      Simulation playback stream
ws://.../ws/alerts                    System-wide alert channel
```

## 16.2 14-Week Development Roadmap

```
PHASE 0 — FOUNDATION  (Weeks 1–2)
──────────────────────────────────────────────────────────────────────
[ ] Monorepo scaffold (Git, CI/CD, Docker Compose)
[ ] PostgreSQL + PostGIS with Indian terrain seed data (SRTM)
[ ] Neo4j + Mission Ontology (OWL 2) import
[ ] Mission data model + FastAPI skeleton
[ ] React frontend scaffold + design system (dark theme)
[ ] Keycloak RBAC setup
[ ] MapLibre GIS base map component

MILESTONE: All team members can develop and test locally.

PHASE 1 — CORE AI ENGINE  (Weeks 3–5)
──────────────────────────────────────────────────────────────────────
[ ] HTN Planner core (Python)
[ ] Rule engine + 20 tactical rules (3 mission types)
[ ] Bayesian threat network (pgmpy, 3 threat types)
[ ] Knowledge graph seeding (200 entities + relations)
[ ] CBR engine + 200 synthetic seed cases (FAISS index)
[ ] COA generation pipeline (3 mission types)
[ ] Constraint satisfaction layer (ACO)
[ ] Explanation object generator

MILESTONE: System generates 3 COAs for any of 3 mission types.

PHASE 2 — SIMULATION ENGINE  (Weeks 6–8)
──────────────────────────────────────────────────────────────────────
[ ] SimPy DES core
[ ] Mesa multi-agent integration
[ ] Terrain physics model (trafficability from DEM)
[ ] Stochastic weather model
[ ] Friendly, Threat, Environment, Judge agent implementations
[ ] Monte Carlo orchestrator (parallel, 16 workers)
[ ] Outcome statistics + failure mode aggregation
[ ] COA scoring engine

MILESTONE: War-game any COA; 500 MC runs in < 2 minutes.

PHASE 3 — DASHBOARD v1  (Weeks 8–10)
──────────────────────────────────────────────────────────────────────
[ ] Main command view (GIS map + situation panel)
[ ] COA comparison screen
[ ] War game playback UI
[ ] Logistics dashboard
[ ] Risk radar visualization (ECharts)
[ ] Commander approval workflow
[ ] Alert system + WebSocket push
[ ] RBAC enforcement in UI

MILESTONE: End-to-end demo — input mission → AI COAs → commander approves.

PHASE 4 — LEARNING & EXPANSION  (Weeks 10–12)
──────────────────────────────────────────────────────────────────────
[ ] Nightly simulation training pipeline
[ ] GNN (BRN) training on simulated data
[ ] Mission memory integration with CBR
[ ] AAR engine + replay UI
[ ] Knowledge graph visualization (D3 force-directed)
[ ] Expand to 6 mission types
[ ] Expand threat library to all 12 threat types
[ ] What-if analysis interface
[ ] Dynamic replanning module (Level 1 + 2)

MILESTONE: Learning loop complete; system improves from simulations.

PHASE 5 — HARDENING & DEMO PREP  (Weeks 12–14)
──────────────────────────────────────────────────────────────────────
[ ] Full integration testing (all services end-to-end)
[ ] Security audit (RBAC, audit chain, encryption)
[ ] Performance optimization (simulation speed, map responsiveness)
[ ] Offline PWA capability
[ ] 3 showcase demo scenarios scripted and rehearsed
[ ] Complete documentation
[ ] Stress testing (concurrent users, simulation load)
[ ] Presentation materials prepared

MILESTONE: Production-quality demo ready for SIH / VITISH.

── FUTURE WORK (Post-Hackathon) ─────────────────────────────────────
[ ] Reinforcement learning for planning weight optimisation
[ ] 3D digital twin (Three.js terrain + entity animation)
[ ] Voice-assisted planning (offline Vosk + military vocabulary)
[ ] Hardware sensor integration (RFID, GPS trackers)
[ ] Inter-operability: MIL-STD-2525 symbology
[ ] Red team AI agent (adversarial simulation)
[ ] Cartosat-DEM integration (ISRO data)
```

---

# 17. INNOVATION FEATURES

## 17.1 Mission Memory with Semantic Compression

Unlike simple case databases, BATMAN stores plans as **128-dimensional graph embeddings** (compressed representations enabling fast vector similarity search). The embedding model is trained via **contrastive learning**: similar missions are pulled closer in embedding space; dissimilar missions pushed apart.

Benefits:
- Millisecond retrieval across 10,000+ cases (FAISS ANN search)
- Generalisation across mission variants
- Transfer learning between related mission types

## 17.2 Operational Readiness Score (ORS)

```
ORS = weighted_avg(
  personnel_readiness(all_units),
  equipment_readiness(all_equipment),
  logistics_readiness(supply_chain),
  comms_readiness(network_state),
  training_currency(all_units)
)

Example output:
  ORS = 0.78  [74% confidence]
  ├── Personnel:  0.91  ✓
  ├── Equipment:  0.83  ✓
  ├── Logistics:  0.64  ⚠ (fuel low in Sector-3)
  ├── Comms:      0.71  ⚠ (relay degraded Sector-3)
  └── Training:   0.89  ✓

AI Advisory: "Address logistics and comms before committing
              this force to a time-critical operation."
```

## 17.3 Terrain Intelligence Module

Dynamic terrain intelligence beyond static maps:

- **Seasonal trafficability**: monsoon, snowpack, road condition updates
- **Natural chokepoint identification**: graph-theoretic bottleneck analysis
- **Ambush suitability surface**: continuous risk raster layer
- **Cover quality gradient**: vegetation + terrain LOS combination
- **Helicopter LZ identification**: automated flat / obstacle-free zone detection

## 17.4 Communications Architecture Planning

For each COA, BATMAN automatically:
- Models RF propagation from terrain obstacle profile
- Identifies RF shadow areas in AOR
- Designs optimal relay network (number, positions)
- Simulates degraded comms scenarios in war game
- Estimates command latency increase under EW threat

## 17.5 Collaborative Planning Mode

Multiple officers simultaneously edit the same mission plan:
- CRDT-based real-time synchronization (no merge conflicts)
- Role-specific view emphasis (Intel vs. Logistics officer views)
- Comment and annotation system on any plan element
- Conflict detection (two edits with contradictory constraints)
- Version control: who changed what, when, why

## 17.6 Voice-Assisted Planning (Offline)

Using offline speech recognition (Vosk + custom military lexicon):
- Voice commands: "Zoom to grid 4378", "What is IED risk on Route Alpha?"
- Voice edits: "Add a QRT to the northern blocking position"
- Completely air-gapped — no network required
- Keeps commander eyes-on-map during planning

## 17.7 Logistics Forecasting Engine

72-hour supply forecast:
- Consumption models (ammo, fuel, rations, water, medical)
- Supply chain lead time by mode and route
- Weather impact on resupply route feasibility
- Alert when stocks reach threshold before resupply arrives
- Optimize resupply schedule to minimize route exposure window

## 17.8 AI-Generated OPORD Draft

After COA approval, BATMAN generates a draft **Operations Order** in standard Indian Army format:
- All annexes auto-populated from plan data (Logistics, Comms, Medical)
- Mission timeline in order format
- Human review + edit + sign-off before issue
- No external LLM — generated entirely from structured templates + plan data

---

# 18. RISK ANALYSIS & CRITICAL EVALUATION

## 18.1 Technical Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| HTN too slow for complex missions | MEDIUM | HIGH | Time-boxing; CBR warm-start; parallel threads |
| GNN insufficient training data (early) | HIGH | MEDIUM | Aggressive synthetic data generation; simpler baseline until data grows |
| MC simulation exceeds time budget | MEDIUM | HIGH | Adaptive sampling (early stop when variance low); GPU acceleration |
| KG query latency at scale | LOW | MEDIUM | Graph partitioning; materialized views; Cypher optimization |
| Terrain data quality in remote areas | HIGH | HIGH | SRTM → Cartosat → low-res fallback chain |
| Simulation fidelity too low | MEDIUM | HIGH | Validate against historical outcomes; sensitivity analysis to expose gaps |

## 18.2 Architectural Weaknesses & Mitigations

**W1: Simulation fidelity vs. speed trade-off**
At 500 MC runs × 3 COAs, there is a strict computational budget.
*Mitigation*: Hierarchical fidelity — fast low-fi simulation for initial screening; high-fi only for top-2 COAs.

**W2: Cold-start problem (CBR)**
A new deployment has no mission history.
*Mitigation*: Pre-populate with 200+ synthetic cases generated by simulation at setup time. Sufficient for early retrieval quality.

**W3: Manually-designed Bayesian network structure**
Expert-designed structure may miss non-obvious causal relationships.
*Mitigation*: Apply structure learning (PC algorithm, hill-climbing) to validate and refine. Expert graph is the prior.

**W4: Rule engine scalability**
Hundreds of rules become hard to maintain and test.
*Mitigation*: Modular rule organization by mission type + doctrine version. Automated regression suite. Conflict detection tooling.

## 18.3 MVP vs. Future Work Matrix

```
PRIORITY MATRIX
══════════════════════════════════════════════════════════════
MODULE                              MVP (SIH)    FUTURE
────────────────────────────────────────────────────────────
HTN Planner (3 mission types)          ✓
COA Generation (3 COAs)                ✓
Monte Carlo War Gaming                 ✓
COA Comparison Dashboard               ✓
Animated GIS Map + Terrain             ✓
Bayesian Threat Assessment             ✓
CBR Engine (seeded 200 cases)          ✓
Rule Engine (20+ rules)                ✓
Commander Approval Workflow            ✓
RBAC + Immutable Audit Log             ✓
Logistics Dashboard (basic)            ✓
Simulation Playback UI                 ✓
──────────────────────────────────────────────────────────
GNN Battlefield Reasoning              ∂        Full v2
Knowledge Graph Visualization          ∂        Full v2
Dynamic Replanning (all levels)        ∂        Full v2
Collaborative Planning                 —        v2
Voice-Assisted Planning                —        v2
3D Digital Twin                        —        v3
Reinforcement Learning                 —        v3
Full AAR Engine                        ∂        Full v2
OPORD Draft Generation                 ∂        Full v2
══════════════════════════════════════════════════════════════
∂ = Partial / simplified for MVP; full version in future scope
```

---

# 19. FUTURE SCOPE

## 19.1 Reinforcement Learning Integration

**Phase 1** (post-hackathon): Train a policy network using **Proximal Policy Optimisation (PPO)** on the simulation environment. The RL agent learns to:
- Select HTN decomposition methods under uncertainty
- Allocate resources across competing objectives dynamically
- Adjust risk tolerance based on mission success probability

The RL policy is used to **tune planning heuristics** — not to replace the HTN planner or remove human control.

## 19.2 3D Digital Twin Visualization

Full 3D terrain in **Three.js + WebGL**:
- Photorealistic terrain (satellite texture + DEM heightmap)
- Animated entity icons on 3D terrain surface
- 3D line-of-sight visualization
- Dynamic lighting (time of day, weather)
- Long-term: VR headset integration for immersive planning

## 19.3 Federated Multi-Domain Operation

BATMAN nodes at Brigade, Division, and Corps:
- Secure, low-bandwidth plan synchronisation protocol
- Conflict resolution for concurrent edits across echelons
- Hierarchical plan propagation (Corps plan constrains Brigade)
- Cross-domain coordination (Land–Air integration, Cyber effects deconfliction)

## 19.4 Red Team AI Agent

An adversarial AI agent that:
- Analyses BATMAN-generated plans for exploitable weaknesses
- Simulates an intelligent adversary applying counter-plans
- Generates threat-perspective plans to stress-test our own COAs
- Provides more rigorous stress testing than random MC sampling

## 19.5 Integration with Indian Defence Systems

- **ADITYA (Army Tactical C2)**: Data exchange via MIL-STD-2525 symbology
- **Bhoomi GIS**: Integration with Indian Army's indigenous GIS platform
- **Defence Cyber Agency feeds**: Cyber threat intelligence ingestion
- **ISRO / NRSC**: Cartosat-DEM, RISAT SAR imagery integration
- **Akash / MRSAM deconfliction**: Airspace management coordination display (read-only, no fire control)

---

# APPENDIX A: ALGORITHMS REFERENCE

## A.1 HTN Planning Complexity

For a domain with `n` primitive tasks, `k` compound tasks, `m` methods per compound task:

- **Worst case**: O(mᵈ × n), where d = decomposition depth
- **BATMAN mitigations**: CBR warm-start (correct methods ranked first, fewer backtracks), constraint pruning (invalid branches cut early), time-boxing (return best plan within budget)

## A.2 Bayesian Update

$$P(T | E_1, E_2, \ldots, E_n) \propto P(T) \times \prod_i P(E_i | T)$$

where P(T) is the threat prior from the threat library, P(Eᵢ|T) is the sensor model likelihood, and the posterior drives COA planning.

## A.3 COA Utility Function (Full)

$$U(COA) = w_s \cdot P(\text{success}) - w_c \cdot \frac{E[\text{cas}]}{C_{max}} - w_t \cdot \frac{t_{obj}}{t_{deadline}} + w_e \cdot \eta + w_f \cdot \phi$$

$$U_{adj}(COA) = U(COA) \times \left(1 - \frac{\sigma(\text{outcome})}{E(\text{outcome})}\right)$$

High-variance plans are penalized even when their mean outcome is good — this implements *risk-averse* decision support by default, matching the commander's preference for robust plans over lucky ones.

## A.4 Path Cost Function

$$cost(e) = w_1 d + w_2 P_{threat} + w_3 t_{exp} + w_4 (1 - c_{cover}) + w_5 \tau_{pen} + w_6 r_{EW}$$

where weights $\mathbf{w}$ are mission-type specific and commander-tunable at planning time.

---

*BATMAN Architecture Document v2.0*
*Prepared for SIH / VITISH Defence Innovation Hackathon*
*Status: Architecture Proposal — For Technical Review*
*All scenarios, unit designations, and operational data in this document are entirely fictional and created for academic/research purposes.*
*This document contains no classified information.*

---
