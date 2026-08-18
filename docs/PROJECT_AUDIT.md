# BATMAN Project Audit Report

## 1. Current Architecture
The repository currently contains a bifurcated architecture:
- **Codebase A (`services/`)**: A microservices-based architecture conforming closely to the BATMAN v2.0 specifications. It consists of multiple independent services (`gateway`, `mission-svc`, `planning-svc`, `threat-svc`, `wargame-svc`) that communicate via REST (and Kafka in the future). It correctly implements the database layer using asyncpg, PostGIS, and UUIDs.
- **Codebase B (`backend/`)**: A monolithic FastAPI backend application seemingly developed in isolation. It uses synchronous SQLAlchemy, Alembic for migrations, and integer IDs for primary keys, directly violating the architecture document.

## 2. Current Services
- `services/gateway`: API Gateway, handles routing, rate limiting, and structured logging.
- `services/mission-svc`: Handles mission CRUD, uses asyncpg and raw SQL to interact with Postgres. Lacks `objectives` endpoints.
- `services/planning-svc`: Implements HTN Planner, Case-Based Reasoning, Constraint Satisfaction (ACO), and COA generation.
- `services/wargame-svc`: Contains the SimPy Digital Twin, Mesa agents, Monte Carlo orchestration, and terrain/weather models.
- `services/threat-svc`: Bayesian network for threat estimation.
- `services/kg-svc`: Neo4j-based knowledge graph service.
- `services/shared`: Contains canonical data contracts (`contracts.py`) shared across services.

## 3. Current Frontend
- Located in `frontend/`.
- Built with React 18, TypeScript, Vite.
- Implements Redux Toolkit for state management (`missionsSlice`, `threatSlice`, `uiSlice`).
- Uses MapLibre for GIS visualization.
- Pages include `COAView.tsx`, `CommandView.tsx`, `LogisticsView.tsx`, `WargameView.tsx`.
- Matches the presentation layer described in the architecture.

## 4. Current Backend
- Located in `backend/` (Codebase B).
- Contains routers for `/missions` and `/objectives`.
- Uses Alembic for database migrations.
- Contains models (`mission.py`, `objective.py`, `user.py`) and schemas.

## 5. AI Modules
- **HTN Planner**: Implemented in `services/planning-svc/htn/`.
- **Constraint Solver**: Implemented in `services/planning-svc/constraint/`.
- **CBR**: Implemented in `services/planning-svc/cbr/`.
- **Bayesian Threat Network**: Implemented in `services/threat-svc/bayesian/`.
- **Digital Twin & Monte Carlo**: Implemented in `services/wargame-svc/`.
- **Knowledge Graph**: Seed scripts in `services/kg-svc/`.

## 6. Duplications and Architecture Violations
- **Duplicated Modules**: `backend/` and `services/mission-svc/` both attempt to manage Mission data.
- **Duplicated APIs**: Both codebases expose `/api/v1/missions` endpoints.
- **Duplicated Models**: `backend/app/models/mission.py` defines a synchronous SQLAlchemy model, while `services/mission-svc` uses raw SQL over asyncpg conforming to `init_schema.sql`.
- **Duplicated Contracts**: Schemas in `backend/app/schemas/` overlap with `services/shared/contracts.py`.
- **Duplicated Databases**: `backend/alembic` creates its own tables violating the `init_schema.sql` (e.g., uses integer IDs instead of UUIDs, missing PostGIS geometry columns).
- **Architecture Violations**: The `backend/` folder represents a monolithic approach with incorrect database schema types (no PostGIS, integer IDs instead of UUIDs). The architecture document strictly defines a microservices structure (`batman-mission-svc`, `batman-gateway`) with UUIDs and PostGIS geometries.

## 7. Missing Integrations & Mismatches
- **Objectives Endpoints**: `services/mission-svc` is missing `/objectives` endpoints which exist in `backend/`. These need to be migrated to `mission-svc`.
- **Frontend/Backend Mismatches**: The frontend likely points to `services/gateway` (port 8080), but objectives CRUD relies on endpoints only present in `backend/`.
- **Broken Imports/Dependency Issues**: Will need to be resolved when merging `backend/` logic into `services/` and deleting `backend/`.
