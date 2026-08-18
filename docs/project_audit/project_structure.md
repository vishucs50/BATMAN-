# Project Structure

## Core Directories

- **services/**: Backend microservices (mission-svc, planning-svc, threat-svc, wargame-svc, kg-svc, gateway, shared)
- **frontend/**: React/Next frontend application
- **ai/**: Independent AI models and pipelines
- **gateway/**: API Gateway (FastAPI) and routing
- **data/**: Database seeds, init scripts, and datasets
- **scripts/**: Utility and test scripts (e.g., test_full_system.py)
- **tests/**: Unit and integration tests
- **infra/**: Docker configurations, compose files, and keycloak setup
- **docs/**: Project documentation and audits

## Breakdown

### Services
- **mission-svc**: Core mission data management
- **planning-svc**: HTN Planner, COA generation, CBR engine
- **threat-svc**: Bayesian network threat assessment
- **wargame-svc**: Monte Carlo simulation, physics, terrain, sensors
- **kg-svc**: Knowledge Graph (Neo4j) interactions
- **gateway**: Main API router and auth middleware

### Frontend
- **src/pages**: WargameView, COAView, LogisticsView, CommandView
- **src/components**: BatmanMap, AppShell
- **src/store**: Redux slices for states

### Infrastructure
- **infra/docker/docker-compose.yml**: Postgres, Neo4j, Redis, Kafka, InfluxDB, MongoDB, Keycloak, GeoServer.

### Tests
- **tests/unit**: Phase 1, Phase 2 test suites
- **scripts/**: E2E pipeline tests (test_ai_pipeline.py)

---
*A complete tree output up to 5 levels deep has been exported to `tree_export.txt`.*
