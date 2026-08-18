# Websocket Inventory

## Backend
- **Endpoint**: `/ws/alerts`
- **Location**: `services/gateway/routers/alerts.py`
- **Responsibilities**: Streams real-time alerts and mission status updates.
- **Events Published**: Alert objects (JSON strings).
- **Events Subscribed**: Client connection/disconnection.

## Frontend
- **Listener**: `CommandView.tsx` uses native `WebSocket` API to connect to `ws://localhost:8080/api/v1/ws/alerts`.
- **Handling**: Updates local state based on received messages.

## Missing Integrations
- Need real-time feeds for Wargame Simulation updates (currently relies on REST polling or static fetches).
- Need bi-directional communication for interactive planning scenarios.
