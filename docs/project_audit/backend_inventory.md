# Backend Inventory

## Services Overview

### 1. Mission Service (`mission-svc`)
- **Responsibilities**: Core mission CRUD, objectives tracking.
- **Dependencies**: Database (Postgres), Shared contracts.
- **API Endpoints**: `/missions`, `/objectives`

### 2. Planning Service (`planning-svc`)
- **Responsibilities**: COA Generation, HTN Planning, CBR, Constraint solving.
- **Dependencies**: Shared contracts.
- **API Endpoints**: `/planning`

### 3. Threat Service (`threat-svc`)
- **Responsibilities**: Bayesian threat estimation, route risk analysis.
- **Dependencies**: `pgmpy`, Shared contracts.
- **API Endpoints**: `/threats`

### 4. Wargame Service (`wargame-svc`)
- **Responsibilities**: Monte Carlo simulations, Mesa-based multi-agent modeling, replay generation.
- **Dependencies**: Mesa, SimPy, Shared contracts.
- **API Endpoints**: `/wargame`

### 5. Knowledge Graph Service (`kg-svc`)
- **Responsibilities**: Interface with Neo4j, GNN reasoning.
- **Dependencies**: Neo4j driver, PyTorch.
- **API Endpoints**: `/kg`

### 6. API Gateway (`gateway`)
- **Responsibilities**: Request routing, authentication, websocket handling.
- **Dependencies**: All internal services, Keycloak.
- **API Endpoints**: Unified `/api/v1` prefix.

### 7. Logistics Service (`logistics`)
- **Responsibilities**: Track resources, fuel, ammo.
- **Integration**: Models exist in `wargame-svc/logistics`, but no standalone microservice running as an API.

### 8. Shared Library (`shared`)
- **Responsibilities**: Pydantic models and API contracts used across services.
- **File**: `services/shared/contracts.py`

### 9. Authentication
- **Responsibilities**: Validating JWT tokens from Keycloak.
- **File**: `services/gateway/middleware/auth.py`
