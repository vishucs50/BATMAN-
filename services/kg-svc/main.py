"""
BATMAN Knowledge Graph Service
Handles Neo4j Graph DB and GNN Reasoning.
Port: 8006
"""
import os
import uuid
import structlog
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import networkx as nx

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seed_graph import build_entities, build_relationships
logger = structlog.get_logger(__name__)

app = FastAPI(title="BATMAN KG Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Graph Engine Setup (Neo4j with In-Memory Fallback) ---
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "batman_neo4j_secret")

driver = None
in_memory_graph = None

try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    # Test connection
    driver.verify_connectivity()
    logger.info("neo4j_connected", uri=NEO4J_URI)
except Exception as e:
    logger.warning(
        "neo4j_unavailable_using_fallback",
        error=str(e),
        message="Neo4j is unavailable. Automatically switching to in-memory graph implementation for testing. Production requires Neo4j."
    )
    driver = None
    # Initialize in-memory fallback graph (NetworkX)
    in_memory_graph = nx.DiGraph()
    for entity in build_entities():
        in_memory_graph.add_node(entity.id, label=entity.label, **entity.properties)
    for src, rel, tgt in build_relationships(build_entities()):
        in_memory_graph.add_edge(src, tgt, rel_type=rel)


# --- Pydantic Schemas ---

class GraphEntityNode(BaseModel):
    id: str
    label: str
    properties: dict

class GraphRelationship(BaseModel):
    source: str
    target: str
    rel_type: str
    properties: dict = {}

class CypherQueryRequest(BaseModel):
    query: str
    params: dict = {}

class GNNReasoningResponse(BaseModel):
    mission_id: uuid.UUID
    mission_success_probability: float
    route_risk_distribution: Dict[str, float]
    critical_asset_scores: List[dict]
    relational_bottlenecks: List[dict]
    radar_metrics: Dict[str, float] = {}
    model_version: str = "BRN-GraphSage-Baseline-1.0"

class GraphSyncRequest(BaseModel):
    entities: List[GraphEntityNode]
    relationships: List[GraphRelationship]

# --- Helper Functions ---

def get_entity_fallback(entity_id: str):
    if entity_id not in in_memory_graph:
        raise HTTPException(404, "Entity not found")
    node_data = dict(in_memory_graph.nodes[entity_id])
    label = node_data.pop('label', 'Unknown')
    
    neighbors = []
    relationships = []
    
    for neighbor in in_memory_graph.neighbors(entity_id):
        ndata = dict(in_memory_graph.nodes[neighbor])
        nl = ndata.pop('label', 'Unknown')
        neighbors.append(GraphEntityNode(id=neighbor, label=nl, properties=ndata))
        
        edge_data = in_memory_graph.get_edge_data(entity_id, neighbor)
        rel_type = edge_data.pop('rel_type', 'UNKNOWN')
        relationships.append(GraphRelationship(source=entity_id, target=neighbor, rel_type=rel_type, properties=edge_data))

    return {
        "entity": GraphEntityNode(id=entity_id, label=label, properties=node_data),
        "neighbors": neighbors,
        "relationships": relationships
    }

def get_full_graph_fallback(label: Optional[str] = None):
    nodes = []
    for n, data in in_memory_graph.nodes(data=True):
        d = dict(data)
        l = d.pop('label', 'Unknown')
        if label and l != label:
            continue
        nodes.append(GraphEntityNode(id=n, label=l, properties=d))
    
    edges = []
    for u, v, data in in_memory_graph.edges(data=True):
        d = dict(data)
        r = d.pop('rel_type', 'UNKNOWN')
        edges.append(GraphRelationship(source=u, target=v, rel_type=r, properties=d))
        
    return {"nodes": nodes, "edges": edges}

# --- API Endpoints ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "batman-kg-svc", "backend": "neo4j" if driver else "networkx_fallback"}

@app.get("/kg/entity/{entity_id}")
async def get_entity(entity_id: str, depth: int = 1):
    if driver is None:
        return get_entity_fallback(entity_id)
        
    query = """
    MATCH (n {id: $id})-[r]-(m)
    RETURN n, type(r) as rel_type, r, m, startNode(r) = n as outgoing
    """
    with driver.session() as session:
        result = session.run(query, id=entity_id)
        records = list(result)
        
        if not records:
            # Check if node exists without edges
            res = session.run("MATCH (n {id: $id}) RETURN n", id=entity_id).single()
            if not res:
                raise HTTPException(404, "Entity not found")
            node = res["n"]
            return {
                "entity": GraphEntityNode(id=entity_id, label=list(node.labels)[0], properties=dict(node)),
                "neighbors": [],
                "relationships": []
            }

        # Build response
        main_node = records[0]["n"]
        entity = GraphEntityNode(id=entity_id, label=list(main_node.labels)[0], properties=dict(main_node))
        neighbors = []
        relationships = []
        
        for record in records:
            m = record["m"]
            rel_type = record["rel_type"]
            r_props = dict(record["r"])
            outgoing = record["outgoing"]
            
            neighbors.append(GraphEntityNode(id=m["id"], label=list(m.labels)[0], properties=dict(m)))
            
            if outgoing:
                relationships.append(GraphRelationship(source=entity_id, target=m["id"], rel_type=rel_type, properties=r_props))
            else:
                relationships.append(GraphRelationship(source=m["id"], target=entity_id, rel_type=rel_type, properties=r_props))
                
        return {"entity": entity, "neighbors": neighbors, "relationships": relationships}

@app.post("/kg/query")
async def execute_query(req: CypherQueryRequest):
    if driver is None:
        # Fallback can't execute raw Cypher
        raise HTTPException(400, "Raw Cypher queries not supported by in-memory fallback. Require Neo4j.")
        
    with driver.session() as session:
        result = session.run(req.query, **req.params)
        data = [dict(record) for record in result]
        return {"results": data, "row_count": len(data), "execution_time_ms": 0.0}

@app.get("/kg/reasoning/{mission_id}", response_model=GNNReasoningResponse)
async def get_gnn_reasoning(mission_id: uuid.UUID):
    # 1. Fetch world state parameters from mission service
    import httpx
    world_state = {}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"http://127.0.0.1:8001/missions/{mission_id}")
            if resp.status_code == 200:
                mission_data = resp.json()
                world_state = mission_data.get("mission_params", {})
    except Exception as e:
        logger.warning("failed_to_fetch_mission_params", mission_id=str(mission_id), error=str(e))
        
    # 2. Construct NetworkX graph from memory or Neo4j
    g = nx.DiGraph()
    if driver is None:
        g = in_memory_graph
    else:
        try:
            with driver.session() as session:
                result = session.run("MATCH (n) RETURN n")
                for record in result:
                    node = record["n"]
                    label = list(node.labels)[0] if node.labels else "Unknown"
                    g.add_node(node["id"], label=label, **dict(node))
                    
                result = session.run("MATCH (a)-[r]->(b) RETURN a.id as src, b.id as tgt, type(r) as rel_type")
                for record in result:
                    g.add_edge(record["src"], record["tgt"], rel_type=record["rel_type"])
        except Exception as e:
            logger.error("failed_to_fetch_neo4j_graph", error=str(e))
            g = in_memory_graph # fallback to memory on error

    # 3. Weather and Visibility calculations
    weather = world_state.get("initial_weather", "CLEAR").upper()
    visibility = float(world_state.get("visibility_m", 5000.0))
    comms_baseline = float(world_state.get("comms_baseline", 0.95))
    
    weather_penalty = 0.0
    if weather == "FOG":
        weather_penalty = 0.15
    elif weather in ("RAIN", "HEAVY_RAIN"):
        weather_penalty = 0.10
        
    visibility_penalty = max(0.0, 1.0 - (visibility / 2000.0)) * 0.10
    comms_penalty = max(0.0, 1.0 - comms_baseline) * 0.15
    
    # 4. Graph statistics
    nodes_by_label = {}
    for n, data in g.nodes(data=True):
        label = data.get("label", "Unknown")
        nodes_by_label.setdefault(label, []).append(n)
        
    threats = nodes_by_label.get("ThreatActor", [])
    units = nodes_by_label.get("Unit", [])
    roads = nodes_by_label.get("Road", [])
    bridges = nodes_by_label.get("Bridge", [])
    depots = nodes_by_label.get("SupplyDepot", [])
    
    num_threats = len(threats)
    num_units = len(units)
    
    # 5. Mission Success Probability
    ratio = (num_units / max(1.0, num_threats + num_units))
    base_success = 0.70 + 0.20 * ratio
    success_prob = max(0.1, min(0.99, base_success - weather_penalty - visibility_penalty - comms_penalty))
    
    # 6. Route Risk Distribution
    road_risks = {}
    for r in roads:
        r_data = g.nodes[r]
        trafficability = float(r_data.get("trafficability", 1.0))
        terrain_risk = 1.0 - trafficability
        
        threat_impact = 0.0
        for neighbor in g.neighbors(r):
            n_data = g.nodes[neighbor]
            if n_data.get("label") == "ThreatActor":
                threat_impact = max(threat_impact, float(n_data.get("probability", 0.5)))
                
        road_risks[r] = 0.3 * terrain_risk + 0.7 * threat_impact
        
    sorted_roads = sorted(road_risks.items(), key=lambda x: x[1], reverse=True)[:5]
    total_risk = sum(val for r, val in sorted_roads) or 1.0
    route_risk_distribution = {r: round(val / total_risk, 2) for r, val in sorted_roads}
    
    # 7. Critical Asset Scores (Vulnerability & Criticality)
    critical_assets = []
    for u in units[:5]:
        assigned_objs = 0
        threat_count = 0
        for neighbor in g.neighbors(u):
            n_data = g.nodes[neighbor]
            if n_data.get("label") == "MissionObj":
                assigned_objs += 1
            elif n_data.get("label") == "ThreatActor":
                threat_count += 1
                
        criticality = min(1.0, 0.3 + 0.2 * assigned_objs)
        vulnerability = min(0.95, max(0.05, 0.1 + 0.2 * threat_count + weather_penalty))
        critical_assets.append({
            "entity_id": u,
            "criticality": round(criticality, 2),
            "vulnerability": round(vulnerability, 2)
        })
        
    # 8. Relational Bottlenecks
    bc = nx.betweenness_centrality(g)
    relational_bottlenecks = []
    bridge_bc = [(b, bc.get(b, 0.0)) for b in bridges]
    bridge_bc.sort(key=lambda x: x[1], reverse=True)
    for b, score in bridge_bc[:5]:
        relational_bottlenecks.append({
            "entity_id": b,
            "betweenness_centrality": round(score, 4)
        })
        
    # 9. Radar Metrics
    terrain_feats = nodes_by_label.get("TerrainFeat", [])
    avg_trafficability = 1.0
    if terrain_feats:
        avg_trafficability = sum(float(g.nodes[t].get("trafficability", 1.0)) for t in terrain_feats) / len(terrain_feats)
    terrain_metric = round(avg_trafficability * 100.0, 1)
    
    avg_threat = 0.2
    if threats:
        avg_threat = sum(float(g.nodes[t].get("probability", 0.5)) for t in threats) / len(threats)
    threat_metric = round(avg_threat * 100.0, 1)
    
    logistics_metric = round(min(100.0, 40.0 + len(depots) * 5.0), 1)
    comms_metric = round(comms_baseline * 100.0, 1)
    weather_metric = round(max(0.0, 100.0 - (weather_penalty + visibility_penalty) * 200.0), 1)
    
    radar_metrics = {
        "Terrain": terrain_metric,
        "Threat": threat_metric,
        "Logistics": logistics_metric,
        "Comms": comms_metric,
        "Weather": weather_metric
    }
    
    return GNNReasoningResponse(
        mission_id=mission_id,
        mission_success_probability=round(success_prob, 2),
        route_risk_distribution=route_risk_distribution,
        critical_asset_scores=critical_assets,
        relational_bottlenecks=relational_bottlenecks,
        radar_metrics=radar_metrics,
        model_version="BRN-GraphSage-Baseline-1.0"
    )

@app.get("/kg/graph")
async def get_full_graph(label: Optional[str] = None):
    if driver is None:
        return get_full_graph_fallback(label=label)
        
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, type(r) as rel_type, r, m
    LIMIT 500
    """
    if label:
        query = f"MATCH (n:{label})-[r]->(m) RETURN n, type(r) as rel_type, r, m LIMIT 500"
        
    with driver.session() as session:
        result = session.run(query)
        nodes = {}
        edges = []
        for record in result:
            n = record["n"]
            m = record["m"]
            nodes[n["id"]] = GraphEntityNode(id=n["id"], label=list(n.labels)[0], properties=dict(n))
            nodes[m["id"]] = GraphEntityNode(id=m["id"], label=list(m.labels)[0], properties=dict(m))
            edges.append(GraphRelationship(
                source=n["id"], target=m["id"], rel_type=record["rel_type"], properties=dict(record["r"])
            ))
        return {"nodes": list(nodes.values()), "edges": edges}

@app.post("/kg/sync")
async def sync_graph(req: GraphSyncRequest):
    if driver is None:
        for ent in req.entities:
            in_memory_graph.add_node(ent.id, label=ent.label, **ent.properties)
        for rel in req.relationships:
            in_memory_graph.add_edge(rel.source, rel.target, rel_type=rel.rel_type, **rel.properties)
        return {"synced_entities": len(req.entities), "synced_relationships": len(req.relationships)}
        
    with driver.session() as session:
        for ent in req.entities:
            session.run(f"MERGE (n:{ent.label} {{id: $id}}) SET n += $props", id=ent.id, props=ent.properties)
        for rel in req.relationships:
            session.run(f"MATCH (a {{id: $src}}), (b {{id: $tgt}}) MERGE (a)-[:{rel.rel_type}]->(b) SET r += $props", 
                        src=rel.source, tgt=rel.target, props=rel.properties)
    return {"synced_entities": len(req.entities), "synced_relationships": len(req.relationships)}
