# BATMAN Architecture Mapping

This document maps the discovered modules to the architecture specified in `BATMAN_Architecture.md`.

## 1. API Gateway
- **Architecture Module**: Orchestration Layer / API Gateway
- **Current Implementation**: `services/gateway/`
- **Dependencies**: Keycloak (Auth), downstream microservices
- **Consumers**: Frontend (`batman-ui`)
- **Status**: **KEEP**
- **Reason**: Aligns perfectly with the microservices architecture.

## 2. Mission Service
- **Architecture Module**: Mission Management
- **Current Implementation**: `services/mission-svc/`
- **Dependencies**: PostgreSQL + PostGIS
- **Consumers**: API Gateway
- **Status**: **KEEP & REFACTOR**
- **Reason**: Conforms to the async DB schema and PostGIS. Needs to absorb the `objectives` endpoints from Codebase B.

## 3. Planning Service
- **Architecture Module**: Mission Planning Engine (HTN, COA Generator, Constraint Solver, CBR)
- **Current Implementation**: `services/planning-svc/`
- **Dependencies**: `services/shared/contracts.py`, Mission DB, Knowledge Graph
- **Consumers**: API Gateway
- **Status**: **KEEP**
- **Reason**: Implements the core AI capabilities correctly.

## 4. War Gaming Service
- **Architecture Module**: War Gaming Engine (Digital Twin, MC Sim)
- **Current Implementation**: `services/wargame-svc/`
- **Dependencies**: Mission DB, Terrain DB
- **Consumers**: API Gateway, Planning Service
- **Status**: **KEEP**
- **Reason**: Accurate simulation engine implementation.

## 5. Threat Service
- **Architecture Module**: Threat Assessment Module (Bayesian Estimator)
- **Current Implementation**: `services/threat-svc/`
- **Dependencies**: `services/shared/contracts.py`
- **Consumers**: API Gateway
- **Status**: **KEEP**
- **Reason**: Accurately implements the Bayesian Threat Estimation Network.

## 6. Monolithic Backend (Codebase B)
- **Architecture Module**: N/A (Conflicts with Mission Service)
- **Current Implementation**: `backend/`
- **Dependencies**: `backend/app/db/`, Alembic
- **Consumers**: None
- **Status**: **REMOVE & MERGE**
- **Reason**: Violates architecture (integer IDs instead of UUIDs, synchronous DB, monolithic structure). Unique logic (like `/objectives` endpoints and user auth dependencies) will be migrated to `services/mission-svc` and `services/gateway` respectively.

## 7. Frontend
- **Architecture Module**: Presentation Layer (Command Dashboard, etc.)
- **Current Implementation**: `frontend/`
- **Dependencies**: React, Vite, MapLibre
- **Consumers**: Commander (End User)
- **Status**: **KEEP**
- **Reason**: Correctly implements the dashboard and UI layers.

## 8. Database Schema
- **Architecture Module**: Data Layer (PostGIS, Neo4j, etc.)
- **Current Implementation**: `data/seeds/init_schema.sql`
- **Dependencies**: None
- **Consumers**: All backend services
- **Status**: **KEEP**
- **Reason**: Source of truth for the DB schema matching the architecture. Alembic migrations in `backend/` will be removed.

## 9. Shared Contracts
- **Architecture Module**: Inter-service communication types
- **Current Implementation**: `services/shared/contracts.py`
- **Dependencies**: None
- **Consumers**: All services
- **Status**: **KEEP**
- **Reason**: Enforces type safety across service boundaries as specified.
