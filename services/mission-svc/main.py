import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
Mission Service — BATMAN
========================
Handles: Mission lifecycle, objectives, constraints, unit assignments.
Port: 8001
"""
from contextlib import asynccontextmanager
from typing import Optional, List
import uuid
from datetime import datetime

import structlog
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = structlog.get_logger(__name__)

DATABASE_URL = "postgresql+asyncpg://batman:batman_dev_secret@localhost:5432/batman"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("mission-svc starting")
    
    # Auto-seed database if empty
    import json
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM missions"))
            count = result.scalar()
            if count == 0:
                logger.info("No missions found. Seeding default mission OP-RED-DAWN...")
                await session.execute(
                    text("""
                        INSERT INTO missions (mission_code, mission_type, classification, mission_params, roe_profile)
                        VALUES (:code, :mtype, :classification, CAST(:params AS jsonb), CAST(:roe AS jsonb))
                    """),
                    {
                        "code": "OP-RED-DAWN",
                        "mtype": "COUNTER_INFILTRATION",
                        "classification": "SECRET",
                        "params": json.dumps({"target": "Hanupatta", "threat_level": "HIGH"}),
                        "roe": json.dumps({"use_of_force": "RETURN_FIRE_ONLY", "civilian_preservation": "STRICT"})
                    }
                )
                await session.commit()
                logger.info("Database successfully seeded.")
        except Exception as e:
            logger.error("Failed to seed database", error=str(e))
            
    yield
    logger.info("mission-svc shutting down")
    await engine.dispose()


app = FastAPI(
    title="BATMAN Mission Service",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── DEPENDENCY ────────────────────────────────────────────────────────────────

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ── SCHEMAS ───────────────────────────────────────────────────────────────────

VALID_MISSION_TYPES = {
    "COUNTER_INFILTRATION", "COUNTER_TERRORISM", "COUNTER_INSURGENCY",
    "CONVOY_PROTECTION", "HIGH_ALTITUDE_LOGISTICS", "HADR",
    "HOSTAGE_RESCUE", "BORDER_SURVEILLANCE", "CRITICAL_INFRA_SECURITY",
}


class MissionCreate(BaseModel):
    mission_code: str = Field(..., min_length=3, max_length=50)
    mission_type: str
    classification: str = "UNCLASSIFIED"
    h_hour: Optional[datetime] = None
    mission_params: dict = {}
    roe_profile: dict = {}


class MissionOut(BaseModel):
    id: uuid.UUID
    mission_code: str
    mission_type: str
    status: str
    classification: str
    created_at: datetime
    updated_at: datetime


class ObjectiveCreate(BaseModel):
    obj_type: str
    priority: int = Field(..., ge=1, le=5)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    target_location: Optional[str] = None


class ObjectiveOut(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID
    obj_type: str
    priority: int
    status: str
    description: Optional[str]
    deadline: Optional[datetime]


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "batman-mission-svc"}


@app.post("/missions", status_code=201)
async def create_mission(payload: MissionCreate, db: AsyncSession = Depends(get_db)):
    if payload.mission_type not in VALID_MISSION_TYPES:
        raise HTTPException(400, f"Invalid mission_type. Valid: {VALID_MISSION_TYPES}")

    import json
    result = await db.execute(
        text("""
            INSERT INTO missions (mission_code, mission_type, classification, mission_params, roe_profile)
            VALUES (:code, :mtype, :classification, CAST(:params AS jsonb), CAST(:roe AS jsonb))
            RETURNING id, mission_code, mission_type, status, classification, created_at, updated_at
        """),
        {
            "code": payload.mission_code,
            "mtype": payload.mission_type,
            "classification": payload.classification,
            "params": json.dumps(payload.mission_params),
            "roe": json.dumps(payload.roe_profile),
        },
    )
    await db.commit()
    row = result.fetchone()
    logger.info("mission_created", mission_code=payload.mission_code, id=str(row.id))
    return dict(row._mapping)


@app.get("/missions")
async def list_missions(
    status: Optional[str] = None,
    mission_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    filters = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}
    if status:
        filters.append("status = :status")
        params["status"] = status
    if mission_type:
        filters.append("mission_type = :mission_type")
        params["mission_type"] = mission_type

    where_clause = " AND ".join(filters)
    result = await db.execute(
        text(f"""
            SELECT id, mission_code, mission_type, status, classification, created_at, updated_at
            FROM missions
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """),
        params,
    )
    rows = result.fetchall()
    return {"missions": [dict(r._mapping) for r in rows], "total": len(rows)}


@app.get("/missions/{mission_id}")
async def get_mission(mission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM missions WHERE id = :id"),
        {"id": str(mission_id)},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Mission not found")
    return dict(row._mapping)


@app.get("/missions/{mission_id}/status")
async def mission_status(mission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """
    Returns live mission status aggregation.
    Phase 0: returns static structure. Phase 1+: joins units, threats, alerts.
    """
    result = await db.execute(
        text("SELECT id, mission_code, status FROM missions WHERE id = :id"),
        {"id": str(mission_id)},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Mission not found")
    return {
        "mission_id": str(mission_id),
        "mission_code": row.mission_code,
        "status": row.status,
        "phase": 0,
        "units": [],
        "active_threats": [],
        "alerts": [],
        "note": "Full status available in Phase 1",
    }


@app.post("/missions/{mission_id}/objectives", status_code=201)
async def create_objective(
    mission_id: uuid.UUID,
    payload: ObjectiveCreate,
    db: AsyncSession = Depends(get_db)
):
    import json
    result = await db.execute(
        text("""
            INSERT INTO objectives (mission_id, obj_type, priority, description, deadline, target_location)
            VALUES (:mission_id, :obj_type, :priority, :description, :deadline, 
                CASE WHEN :target_location IS NOT NULL THEN ST_GeomFromText(:target_location, 4326) ELSE NULL END)
            RETURNING id, mission_id, obj_type, priority, status, description, deadline
        """),
        {
            "mission_id": str(mission_id),
            "obj_type": payload.obj_type,
            "priority": payload.priority,
            "description": payload.description,
            "deadline": payload.deadline,
            "target_location": payload.target_location
        }
    )
    await db.commit()
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Mission not found or error creating objective")
    return dict(row._mapping)


@app.get("/missions/{mission_id}/objectives")
async def list_objectives(mission_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT id, mission_id, obj_type, priority, status, description, deadline 
            FROM objectives 
            WHERE mission_id = :mission_id 
            ORDER BY priority ASC, id ASC
        """),
        {"mission_id": str(mission_id)}
    )
    rows = result.fetchall()
    return [dict(r._mapping) for r in rows]


@app.get("/objectives/{objective_id}")
async def get_objective(objective_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("""
            SELECT id, mission_id, obj_type, priority, status, description, deadline 
            FROM objectives 
            WHERE id = :objective_id
        """),
        {"objective_id": str(objective_id)}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Objective not found")
    return dict(row._mapping)
