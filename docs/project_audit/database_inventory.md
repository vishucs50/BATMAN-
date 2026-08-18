# Database Inventory

## Data Stores
1. **PostgreSQL / PostGIS**
   - **Service Name**: `batman-postgres`
   - **Port**: 5432
   - **Purpose**: Relational data, GIS data (terrain, features)

2. **Neo4j**
   - **Service Name**: `batman-neo4j`
   - **Port**: 7687 / 7474
   - **Purpose**: Knowledge graph, relational reasoning, GNN processing

3. **Redis**
   - **Service Name**: `batman-redis`
   - **Port**: 6379
   - **Purpose**: Caching, real-time message broker

4. **InfluxDB**
   - **Service Name**: `batman-influxdb`
   - **Port**: 8086
   - **Purpose**: Time series data, sensor telemetry

5. **MongoDB**
   - **Service Name**: `batman-mongodb`
   - **Port**: 27017
   - **Purpose**: Document store for Mission Memory (AAR)

## Database Artifacts
- **Seed Data / Migrations**:
  - `data/seeds/init_schema.sql` (mapped to PostgreSQL via docker-compose)
  - `services/kg-svc/seed_graph.py` (Neo4j seed script)
- **Schemas / Tables / Indexes**:
  - Outlined in `init_schema.sql` (mission tables, objective tables).
  - Graph schema is dynamically created by `seed_graph.py` (Unit, ThreatActor, TerrainFeat, etc.).
