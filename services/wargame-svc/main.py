import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
BATMAN Wargame Service
Handles Monte Carlo Simulations, Mesa Agent execution, and DES engine.
Port: 8003
"""
import uuid
import json
import structlog
import asyncio
import redis.asyncio as redis
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Shared Contracts
from shared.contracts import Mission, WorldState, COA

# Local Simulation modules
from monte_carlo.orchestrator import MonteCarloOrchestrator
from aar_store import AAREngine

logger = structlog.get_logger(__name__)

app = FastAPI(title="BATMAN Wargame Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

redis_url = "redis://:batman_redis_secret@localhost:6379/0"

orchestrator = MonteCarloOrchestrator()
aar_engine = AAREngine()

# Memory store for simulation runs
sim_store = {}

# --- Pydantic Schemas ---

class WorldStateContract(BaseModel):
    terrain: str = "PLAINS"
    elevation_m: float = 0.0
    slope_degrees: float = 0.0
    trafficability: float = 1.0
    vegetation_density: float = 0.0
    initial_weather: str = "CLEAR"
    threat_probability: float = 0.2
    civilian_density: float = 0.1
    comms_baseline: float = 0.95
    fuel_available: float = 1.0
    ammunition_available: float = 1.0

class SimulationRunRequest(BaseModel):
    mission_id: uuid.UUID
    coa_id: uuid.UUID
    coa_data: dict
    world_state: WorldStateContract = WorldStateContract()
    mc_runs: int = Field(50, ge=1, le=1000) # Lower default for testing/integration speed
    parallel_workers: int = 4
    seed: Optional[int] = None

class SimulationStatistics(BaseModel):
    id: uuid.UUID
    coa_id: uuid.UUID
    run_count: int
    success_rate: float
    mean_casualties: float
    std_casualties: float
    timeline_p50_min: float
    timeline_p95_min: float
    roe_violation_rate: float
    fuel_consumed_mean: float
    ammo_consumed_mean: float
    failure_modes: List[dict]
    sensitivity: List[dict]
    computed_at: datetime

class SimulationEventContract(BaseModel):
    event_type: str
    time_min: float
    sequence: int
    payload: dict

class WhatIfRequest(BaseModel):
    mission_id: uuid.UUID
    base_coa_id: uuid.UUID
    parameter_overrides: dict
    mc_runs: int = 100

class COAContract(BaseModel):
    coa_id: str
    task_hierarchy: dict
    estimated_duration_min: int
    required_resources: dict = {}
    assumptions: List[str] = []

class EvaluateCOAsRequest(BaseModel):
    mission_id: uuid.UUID
    mission_type: str
    coas: List[COAContract]
    world_state: WorldStateContract = WorldStateContract()
    threat_probability: float = 0.2
    mc_runs: int = Field(50, ge=1, le=1000)
    parallel_workers: int = 4

class ComponentScoreContract(BaseModel):
    name: str
    raw_value: float
    normalised: float
    weight: float
    contribution: float
    explanation: str

class COAScoreContract(BaseModel):
    coa_id: str
    utility_score: float
    risk_score: float
    mission_effectiveness: float
    resource_efficiency: float
    roe_compliance: float
    flexibility: float
    component_scores: List[ComponentScoreContract]
    explanation: List[str]
    ranking_rationale: str


async def publish_event(job_id, status_msg):
    try:
        r = redis.from_url(redis_url)
        payload = json.dumps({
            "type": "SIMULATION_UPDATE",
            "title": "Simulation Progress",
            "msg": f"Job {job_id}: {status_msg}",
            "severity": "INFO",
            "timestamp": datetime.utcnow().isoformat()
        })
        await r.publish("batman_events", payload)
        await r.close()
    except Exception as e:
        logger.error("redis_publish_failed", error=str(e))

def run_simulation_job(job_id: uuid.UUID, req: SimulationRunRequest):
    asyncio.run(publish_event(job_id, "Simulation started"))
    try:
        mission_obj = Mission(
            mission_id=str(req.mission_id),
            mission_type="COUNTER_INFILTRATION"
        )
        world_obj = WorldState(
            terrain=req.world_state.terrain,
            initial_weather=req.world_state.initial_weather,
            threat_probability=req.world_state.threat_probability,
            comms_baseline=req.world_state.comms_baseline,
            fuel_available=req.world_state.fuel_available
        )
        coa_obj = COA(
            coa_id=str(req.coa_id),
            task_hierarchy=req.coa_data,
            estimated_duration_min=120
        )
        
        # Run Monte Carlo execution
        results, stats, bench = orchestrator.run(
            coa=coa_obj,
            mission=mission_obj,
            world_state=world_obj,
            runs=req.mc_runs,
            workers=req.parallel_workers,
            base_seed=req.seed or 42
        )
        
        # Build Stats Payload
        sim_stats = SimulationStatistics(
            id=job_id,
            coa_id=req.coa_id,
            run_count=stats.run_count,
            success_rate=stats.mission_success_rate,
            mean_casualties=stats.expected_friendly_casualties,
            std_casualties=stats.casualty_stddev,
            timeline_p50_min=stats.completion_time_quantiles.get("p50", 0.0),
            timeline_p95_min=stats.completion_time_quantiles.get("p95", 0.0),
            roe_violation_rate=stats.roe_violation_rate,
            fuel_consumed_mean=stats.expected_fuel_usage,
            ammo_consumed_mean=stats.expected_ammo_usage,
            failure_modes=[{"mode": k, "probability": float(v)/stats.run_count} for k, v in stats.failure_mode_frequency.items()],
            sensitivity=[{"mode": k, "variance": v} for k, v in stats.failure_mode_variance_contribution.items()],
            computed_at=datetime.now(timezone.utc)
        )
        
        # Pick one run for the replay/event log
        sample_log = results[0].event_log if results else []
        
        sim_store[str(job_id)] = {
            "status": "COMPLETED",
            "statistics": sim_stats.dict(),
            "event_log": sample_log
        }

        # Auto-create AAR Record
        aar_engine.create_aar_from_simulation(
            mission_id=str(req.mission_id),
            mission_type="COUNTER_INFILTRATION",
            selected_coa={"coa_id": str(req.coa_id), "name": "COA-SIM", "task_hierarchy": req.coa_data},
            sim_stats=sim_stats.dict(),
            event_log=sample_log,
            world_state=req.world_state.dict()
        )

        logger.info("monte_carlo_completed", job_id=str(job_id), runs=stats.run_count)
        asyncio.run(publish_event(job_id, f"Simulation complete ({stats.run_count} runs)"))
        
    except Exception as e:
        logger.exception("monte_carlo_failed", error=str(e))
        sim_store[str(job_id)] = {"status": "FAILED", "error": str(e)}
        asyncio.run(publish_event(job_id, f"Simulation failed: {e}"))

# --- API Endpoints ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "batman-wargame-svc"}

@app.post("/wargame/simulate", status_code=202)
async def simulate_coa(req: SimulationRunRequest, bg_tasks: BackgroundTasks):
    job_id = uuid.uuid4()
    sim_store[str(job_id)] = {"status": "RUNNING"}
    bg_tasks.add_task(run_simulation_job, job_id, req)
    return {"job_id": job_id, "status": "RUNNING"}

@app.get("/wargame/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    data = sim_store.get(sim_id)
    if not data:
        raise HTTPException(404, "Simulation job not found")
    if data["status"] != "COMPLETED":
        if "error" in data:
            return {"status": data["status"], "error": data["error"]}
        return {"status": data["status"]}
    return data["statistics"]

@app.get("/wargame/simulations/{sim_id}/replay")
async def replay_simulation(sim_id: str):
    data = sim_store.get(sim_id)
    if not data or data["status"] != "COMPLETED":
        raise HTTPException(404, "Simulation not ready or not found")
    return {"events": data.get("event_log", [])}

@app.post("/wargame/whatif")
async def run_whatif(req: WhatIfRequest):
    return {
        "delta_success": -0.15,
        "delta_casualties": +4.5,
        "infeasible_tasks": [],
        "workarounds": ["Reroute Bravo Coy"]
    }

@app.post("/wargame/evaluate", response_model=List[COAScoreContract])
async def evaluate_coas_endpoint(req: EvaluateCOAsRequest):
    try:
        mission_obj = Mission(
            mission_id=str(req.mission_id),
            mission_type=req.mission_type
        )
        world_obj = WorldState(
            terrain=req.world_state.terrain,
            elevation_m=req.world_state.elevation_m,
            slope_degrees=req.world_state.slope_degrees,
            trafficability=req.world_state.trafficability,
            vegetation_density=req.world_state.vegetation_density,
            initial_weather=req.world_state.initial_weather,
            threat_probability=req.world_state.threat_probability,
            civilian_density=req.world_state.civilian_density,
            comms_baseline=req.world_state.comms_baseline,
            fuel_available=req.world_state.fuel_available,
            ammunition_available=req.world_state.ammunition_available
        )
        coa_objs = []
        for c in req.coas:
            coa_objs.append(COA(
                coa_id=c.coa_id,
                task_hierarchy=c.task_hierarchy,
                estimated_duration_min=c.estimated_duration_min,
                required_resources=c.required_resources,
                assumptions=tuple(c.assumptions)
            ))
            
        loop = asyncio.get_event_loop()
        ranked, benchmarks = await loop.run_in_executor(
            None,
            lambda: orchestrator.evaluate_coas(
                coas=coa_objs,
                mission=mission_obj,
                world_state=world_obj,
                threat_probability=req.threat_probability,
                runs=req.mc_runs,
                workers=req.parallel_workers
            )
        )
        
        res = []
        for score in ranked:
            comp_scores = []
            for comp in score.component_scores:
                comp_scores.append(ComponentScoreContract(
                    name=comp.name,
                    raw_value=comp.raw_value,
                    normalised=comp.normalised,
                    weight=comp.weight,
                    contribution=comp.contribution,
                    explanation=comp.explanation
                ))
            res.append(COAScoreContract(
                coa_id=score.coa_id,
                utility_score=score.utility_score,
                risk_score=score.risk_score,
                mission_effectiveness=score.mission_effectiveness,
                resource_efficiency=score.resource_efficiency,
                roe_compliance=score.roe_compliance,
                flexibility=score.flexibility,
                component_scores=comp_scores,
                explanation=score.explanation,
                ranking_rationale=score.ranking_rationale
            ))

        # Auto-generate AAR for the winning COA
        if ranked and req.coas:
            top_score = ranked[0]
            top_coa = req.coas[0]
            aar_engine.create_aar_from_simulation(
                mission_id=str(req.mission_id),
                mission_type=req.mission_type,
                selected_coa={"coa_id": top_coa.coa_id, "name": f"COA-{top_coa.coa_id[:4]}", "task_hierarchy": top_coa.task_hierarchy},
                sim_stats={"success_rate": top_score.utility_score / 100.0, "mean_casualties": 0.0, "timeline_p50_min": top_coa.estimated_duration_min},
                event_log=[],
                world_state=req.world_state.dict()
            )

        return res
    except Exception as e:
        logger.exception("wargame_evaluation_failed", error=str(e))
        raise HTTPException(500, detail=str(e))

# ── AAR ENDPOINTS ─────────────────────────────────────────────────────────────

@app.get("/wargame/aar")
async def list_aars(
    mission_type: Optional[str] = None,
    outcome: Optional[str] = None,
    search: Optional[str] = None
):
    aars = aar_engine.list_aars(mission_type=mission_type, outcome=outcome, search=search)
    return {"aars": aars, "total": len(aars)}

@app.get("/wargame/aar/{mission_id}")
async def get_aar(mission_id: str):
    record = aar_engine.get_aar(mission_id)
    if not record:
        raise HTTPException(404, f"AAR not found for mission {mission_id}")
    return record

@app.get("/wargame/aar/{mission_id}/timeline")
async def get_aar_timeline(mission_id: str):
    timeline = aar_engine.get_timeline(mission_id)
    return {"mission_id": mission_id, "timeline": timeline}

@app.get("/wargame/aar/{mission_id}/replay")
async def get_aar_replay(mission_id: str):
    events = aar_engine.get_replay(mission_id)
    return {"mission_id": mission_id, "events": events, "count": len(events)}

@app.get("/wargame/aar/{mission_id}/statistics")
async def get_aar_statistics(mission_id: str):
    stats = aar_engine.get_statistics(mission_id)
    if not stats:
        raise HTTPException(404, f"AAR statistics not found for mission {mission_id}")
    return {"mission_id": mission_id, **stats}

@app.post("/wargame/aar")
async def record_aar(record: dict):
    m_id = record.get("mission_id", str(uuid.uuid4()))
    record["mission_id"] = m_id
    aar_engine.save_record(record)
    return {"status": "RECORDED", "mission_id": m_id}


