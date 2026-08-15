# BATMAN — Battlefield Analytics & Tactical Mission Assistance Network
### v2.0 | Indigenous AI Command Decision Support System

> **An AI-powered mission planning and decision support system for the Indian Armed Forces.**
> The AI plans and simulates — the Human Commander decides and commands.

---

## Project Structure

```
batman/
├── frontend/          # React 18 + TypeScript + MapLibre GL command dashboard
├── services/          # Python FastAPI microservices
│   ├── gateway/       # API gateway (auth, rate-limiting)
│   ├── mission-svc/   # Mission lifecycle management
│   ├── planning-svc/  # HTN planner + COA generator
│   ├── wargame-svc/   # Monte Carlo simulation engine
│   ├── threat-svc/    # Bayesian threat assessment
│   ├── kg-svc/        # Knowledge graph (Neo4j)
│   ├── gis-svc/       # Spatial analysis (PostGIS + GDAL)
│   ├── logistics-svc/ # Resource tracking
│   ├── sa-svc/        # Situation awareness fusion
│   ├── learn-svc/     # Offline training pipeline
│   ├── aar-svc/       # After action review
│   └── audit-svc/     # Immutable decision audit
├── ai/                # Shared AI modules + model registry
├── data/              # Terrain, doctrine, threat library, seed data
├── infra/             # Docker, K8s, Helm
└── tests/             # Unit, integration, simulation validation
```

## Quick Start (Development)

```bash
# 1. Prerequisites: Docker + Docker Compose, Node 20+, Python 3.12+
# 2. Start all infrastructure services
docker compose -f infra/docker/docker-compose.yml up -d

# 3. Start backend services (from each service dir)
cd services/gateway && uvicorn main:app --reload --port 8080

# 4. Start frontend
cd frontend && npm install && npm run dev
```

## Phase 0 Status (Foundation)
- [x] Monorepo scaffold + Git
- [x] Docker Compose (PostgreSQL/PostGIS, Neo4j, Redis, Kafka, InfluxDB)
- [x] Mission data model + FastAPI skeleton (gateway + mission-svc)
- [x] React frontend + design system (dark theme)
- [x] MapLibre GIS base map component
- [x] Mission Ontology (OWL 2)
- [x] Database schema (PostgreSQL + PostGIS)
- [x] Keycloak RBAC configuration
- [ ] Indian terrain seed data (SRTM — run `data/seeds/load_terrain.sh`)

## Architecture Reference
See [`BATMAN_Architecture.md`](./BATMAN_Architecture.md) for full technical design.

---
*Classification: UNCLASSIFIED — Academic/Research Purpose Only*
*Prepared for SIH / VITISH Defence Innovation Hackathon*
