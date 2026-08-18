# Frontend Inventory

## Framework
- React + TypeScript (Vite based)

## Pages & Routes
- `CommandView.tsx` - Main Commander Dashboard
- `WargameView.tsx` - Wargame & Digital Twin Simulation
- `COAView.tsx` - COA Selection and Generation
- `LogisticsView.tsx` - Resource and Asset tracking

## Key Components
- `components/map/BatmanMap.tsx` - Geospatial / GIS visualization
- `components/shared/AppShell.tsx` - Main application layout
- `App.tsx` - Main router definitions

## Dashboard Widgets (Conceptual)
- Mission Status Panel
- Threat Assessment Map Layer
- Simulation Replay Controls
- Alerts Feed

## API Integrations
*(via Redux Slices using Axios)*
- `missionsSlice.ts`:
  - `GET /api/v1/missions`
  - `GET /api/v1/missions/{id}`
  - `GET /api/v1/missions/{id}/coas`
  - `POST /api/v1/missions/{id}/coas/generate`
  - `POST /api/v1/missions/{id}/coas/{coaId}/approve`
  - `POST /api/v1/missions/{id}/coas/{coaId}/simulate`
- `kgSlice.ts`:
  - `GET /api/v1/gis/reasoning/{id}`
  - `GET /api/v1/gis/graph`
- `wargameSlice.ts`:
  - `GET /api/v1/simulation/{simId}`
- `threatSlice.ts`:
  - `GET /api/v1/threats/missions/{id}`

## Websockets
- Connection: `ws://localhost:8080/api/v1/ws/alerts` initialized in `CommandView.tsx`.
- Real or Placeholder: Data is currently mocked/placeholder in some slices; real websocket connection exists but event processing is basic.
