"""Deterministic, fictional Phase 1 battlefield graph seed for Neo4j.

The seeder creates 200 entities and a connected relationship set without placing
operationally meaningful locations or real unit data in the repository.
"""
from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class GraphEntity:
    id: str
    label: str
    properties: dict


def build_entities() -> list[GraphEntity]:
    specs = [
        ("Unit", 45, "unit"), ("Road", 30, "road"), ("TerrainFeat", 35, "terrain"),
        ("Bridge", 12, "bridge"), ("Sensor", 20, "sensor"), ("ThreatActor", 18, "threat"),
        ("MissionObj", 16, "objective"), ("SupplyDepot", 12, "depot"), ("ObservationPost", 12, "op"),
    ]
    entities: list[GraphEntity] = []
    for label, count, prefix in specs:
        for index in range(1, count + 1):
            properties = {"id": f"{prefix}-{index:03d}", "name": f"Fictional {label} {index:03d}", "status": "GREEN" if label == "Unit" else "ACTIVE"}
            if label == "TerrainFeat":
                properties.update({"type": ("FORESTED", "MOUNTAINOUS", "URBAN", "HIGH_ALTITUDE")[index % 4], "trafficability": round(.35 + (index % 6) * .1, 2)})
            if label == "ThreatActor":
                properties.update({"type": ("INFILTRATION", "AMBUSH", "IED")[index % 3], "probability": round(.1 + (index % 7) * .1, 2)})
            entities.append(GraphEntity(properties["id"], label, properties))
    assert len(entities) == 200
    return entities


def build_relationships(entities: list[GraphEntity]) -> list[tuple[str, str, str]]:
    ids_by_label: dict[str, list[str]] = {}
    for entity in entities:
        ids_by_label.setdefault(entity.label, []).append(entity.id)
    relations: list[tuple[str, str, str]] = []
    for index, unit in enumerate(ids_by_label["Unit"]):
        relations.append((unit, "POSITIONED_AT", ids_by_label["TerrainFeat"][index % 35]))
        relations.append((unit, "ASSIGNED_TO", ids_by_label["MissionObj"][index % 16]))
    for index, road in enumerate(ids_by_label["Road"]):
        relations.append((road, "PASSES_THROUGH", ids_by_label["TerrainFeat"][index % 35]))
        relations.append((road, "HAS_RISK", ids_by_label["ThreatActor"][index % 18]))
    for index, sensor in enumerate(ids_by_label["Sensor"]):
        relations.append((sensor, "OBSERVES", ids_by_label["TerrainFeat"][index % 35]))
    for index, threat in enumerate(ids_by_label["ThreatActor"]):
        relations.append((threat, "THREATENS", ids_by_label["Bridge"][index % 12]))
        relations.append((threat, "LOCATED_IN", ids_by_label["TerrainFeat"][index % 35]))
    for index, depot in enumerate(ids_by_label["SupplyDepot"]):
        relations.append((depot, "SUPPORTS", ids_by_label["Unit"][index % 45]))
    for index, op in enumerate(ids_by_label["ObservationPost"]):
        relations.append((op, "OVERWATCHES", ids_by_label["Road"][index % 30]))
    return relations


def seed(uri: str | None = None, username: str | None = None, password: str | None = None) -> dict[str, int]:
    """Upsert all data, keeping graph access within this service module."""
    try:
        from neo4j import GraphDatabase
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("neo4j driver is required to seed the knowledge graph") from error
    entities = build_entities(); relationships = build_relationships(entities)
    driver = GraphDatabase.driver(uri or getenv("NEO4J_URI", "bolt://localhost:7687"), auth=(username or getenv("NEO4J_USER", "neo4j"), password or getenv("NEO4J_PASSWORD", "batman_neo4j_secret")))
    with driver.session() as session:
        for entity in entities:
            session.run(f"MERGE (n:{entity.label} {{id: $id}}) SET n += $properties", id=entity.id, properties=entity.properties)
        for source, rel_type, target in relationships:
            session.run(f"MATCH (a {{id: $source}}), (b {{id: $target}}) MERGE (a)-[:{rel_type}]->(b)", source=source, target=target)
    driver.close()
    return {"entities": len(entities), "relationships": len(relationships)}


if __name__ == "__main__":
    print(seed())
