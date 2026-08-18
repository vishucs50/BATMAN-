# Docker Inventory

## Docker Compose Services (`infra/docker/docker-compose.yml`)

1. **`postgres`**
   - Image: `postgis/postgis:16-3.4`
   - Ports: `5432:5432`
   - Volumes: `postgres_data`, `init_schema.sql`

2. **`neo4j`**
   - Image: `neo4j:5.20-community`
   - Ports: `7474:7474`, `7687:7687`
   - Volumes: `neo4j_data`, `neo4j_logs`

3. **`redis`**
   - Image: `redis:7-alpine`
   - Ports: `6379:6379`
   - Volumes: `redis_data`

4. **`zookeeper` & `kafka`**
   - Image: `confluentinc/cp-zookeeper:7.6.0`, `confluentinc/cp-kafka:7.6.0`
   - Ports: `9092:9092`
   - Volumes: `zookeeper_data`, `kafka_data`

5. **`influxdb`**
   - Image: `influxdb:2.7-alpine`
   - Ports: `8086:8086`
   - Volumes: `influxdb_data`

6. **`mongodb`**
   - Image: `mongo:7.0`
   - Ports: `27017:27017`
   - Volumes: `mongodb_data`

7. **`keycloak`**
   - Image: `quay.io/keycloak/keycloak:24.0`
   - Ports: `8443:8080`
   - Volumes: `batman-realm.json`

8. **`geoserver`**
   - Image: `kartoza/geoserver:2.25.0`
   - Ports: `8090:8080`
   - Volumes: `geoserver_data`

## Networks
- Default Docker Compose bridge network

## Volumes
- `postgres_data`
- `neo4j_data`
- `neo4j_logs`
- `redis_data`
- `zookeeper_data`
- `kafka_data`
- `influxdb_data`
- `mongodb_data`
- `geoserver_data`
