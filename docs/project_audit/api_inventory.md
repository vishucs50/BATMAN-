# API Inventory

## Mission Service (`mission-svc`)
- **GET /health** - Healthcheck
- **POST /missions** - Create mission (`MissionCreate` -> `MissionOut`)
- **GET /missions** - List missions
- **GET /missions/{mission_id}** - Get mission details
- **GET /missions/{mission_id}/status** - Get live status
- **POST /missions/{mission_id}/objectives** - Add objective (`ObjectiveCreate` -> `ObjectiveOut`)
- **GET /missions/{mission_id}/objectives** - List objectives
- **GET /objectives/{objective_id}** - Get specific objective

## Planning Service (`planning-svc`)
- **GET /health** - Healthcheck
- **POST /planning/coa/generate** - Generate COAs (`COAGenerationRequest` -> `COAResponse`)
- **GET /planning/jobs/{job_id}** - Get planning job status
- **GET /planning/missions/{mission_id}/coa** - List COAs
- **GET /planning/missions/{mission_id}/coa/{coa_id}** - Get specific COA
- **PUT /planning/missions/{mission_id}/coa/{coa_id}** - Update COA
- **POST /planning/missions/{mission_id}/coa/{coa_id}/approve** - Approve COA (`COAApprovalRequest`)
- **POST /planning/missions/{mission_id}/coa/{coa_id}/reject** - Reject COA
- **POST /planning/missions/{mission_id}/replan** - Replan mission (`DynamicReplanRequest`)

## Threat Service (`threat-svc`)
- **GET /health** - Healthcheck
- **GET /threats** - List threats (`ThreatModelSpec`)
- **GET /threats/{threat_id}** - Get specific threat
- **POST /threats/assess** - Run threat assessment (`ThreatAssessmentRequest` -> `ThreatAssessmentResponse`)
- **GET /threats/missions/{mission_id}** - Get threats for mission
- **POST /threats/route-risk** - Calculate route risk (`RouteRiskRequest`)

## Wargame Service (`wargame-svc`)
- **GET /health** - Healthcheck
- **POST /wargame/simulate** - Run Monte Carlo simulation (`SimulationRunRequest`)
- **GET /wargame/simulations/{sim_id}** - Get simulation results (`SimulationStatistics`)
- **GET /wargame/simulations/{sim_id}/replay** - Get simulation replay events (`SimulationEventContract`)
- **POST /wargame/whatif** - Run What-If simulation (`WhatIfRequest`)

## Knowledge Graph Service (`kg-svc`)
- **GET /health** - Healthcheck
- **GET /kg/entity/{entity_id}** - Get entity (`GraphEntityNode`)
- **POST /kg/query** - Run cypher query (`CypherQueryRequest`)
- **GET /kg/reasoning/{mission_id}** - Run GNN reasoning (`GNNReasoningResponse`)
- **GET /kg/graph** - Get graph subset (`GraphRelationship`)
- **POST /kg/sync** - Sync graph (`GraphSyncRequest`)

## API Gateway (`gateway`)
- Proxies endpoints with `/api/v1` prefix to underlying services (e.g., `/missions`, `/health/ready`, `/threats`, `/alerts`, `/audit`)
