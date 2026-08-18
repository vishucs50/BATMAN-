import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
BATMAN Planning Service (Phase 1 AI Integration)
Handles HTN Mission Decomposition, COA Generation, Rule Engine validation.
Port: 8002
"""
import uuid
import structlog
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Shared Contracts
from shared.contracts import WorldState

# Local AI modules
from htn.planner import HTNPlanner
from htn.mission_domains import build_phase_one_domain
from htn.models import WorldState as HTNWorldState

from coa.generator import COAGenerator
from coa.explanations import ExplanationGenerator
from rules.engine import RuleEngine, phase_one_rules
from cbr.engine import CaseBasedReasoner, Case

logger = structlog.get_logger(__name__)

app = FastAPI(title="BATMAN Planning Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Path for storing mission memory cases
CBR_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "cbr", "cases_v1.jsonl"))

# Instantiate the deterministic AI baseline (No pretrained weights found)
domain = build_phase_one_domain()
planner = HTNPlanner(domain=domain)
rule_engine = RuleEngine(rules=phase_one_rules())
cbr = CaseBasedReasoner()
cbr.index(CaseBasedReasoner.synthetic_seed_cases())
cbr.load_index(CBR_DATA_PATH)
coa_generator = COAGenerator(planner=planner, rule_engine=rule_engine, cbr=cbr)
explanation_generator = ExplanationGenerator()

# Memory store for generated COAs (since we're replacing placeholders)
# In production, this would go to Postgres
coa_store = {}
job_store = {}

# --- Pydantic Schemas ---

class Objective(BaseModel):
    id: uuid.UUID
    type: str
    target: dict
    priority: int = Field(..., ge=1, le=5)
    deadline: Optional[datetime] = None
    state: str = "PENDING"

class ConstraintOverride(BaseModel):
    type: str
    category: str
    predicate: str
    penalty: float = 0.0

class COAGenerationRequest(BaseModel):
    mission_id: uuid.UUID
    mission_type: str
    objectives: List[Objective] = []
    constraints: List[ConstraintOverride] = []
    weights: Dict[str, float] = {
        "p_success": 0.35, "casualties": 0.25, "time": 0.15,
        "resource": 0.10, "risk_concentration": 0.08,
        "roe_compliance": 0.04, "flexibility": 0.03
    }
    styles: List[str] = ["BOLD", "BALANCED", "CAUTIOUS"]
    world_state: Optional[dict] = None

class ExplanationObject(BaseModel):
    decision: str
    primary_reasons: List[str]
    supporting_evidence: List[str]
    rule_firings: List[str]
    cbr_matches: List[str]
    risk_factors: List[str]
    alternatives: List[dict]
    confidence: float
    uncertainty_sources: List[str]
    model_version: str

class COAResponse(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID
    coa_number: int
    name: str
    style: str
    status: str = "DRAFT"
    plan_graph: dict
    resource_plan: dict
    timeline: dict
    utility_score: float
    risk_adjusted_score: float
    explanation: Optional[ExplanationObject] = None
    created_at: datetime

class COAApprovalRequest(BaseModel):
    actor_id: uuid.UUID
    actor_role: str
    rationale: str
    modifications: Optional[dict] = None

class DynamicReplanRequest(BaseModel):
    mission_id: uuid.UUID
    current_coa_id: uuid.UUID
    trigger_level: int = Field(..., ge=1, le=3)
    trigger_event: dict
    affected_tasks: List[str] = []

class SimulationOutcome(BaseModel):
    mission_id: uuid.UUID
    coa_id: uuid.UUID
    mission_type: str
    terrain: str
    threat: str
    resources: float
    urgency: float
    success_rate: float
    plan_skeleton: dict
    failure_modes: List[dict] = []

# --- API Endpoints ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "batman-planning-svc"}

@app.post("/planning/coa/generate", status_code=202)
async def generate_coa(req: COAGenerationRequest):
    """Triggers 3-way parallel HTN COA generation."""
    job_id = uuid.uuid4()
    
    # Use real generator
    facts = req.world_state or {}
    facts["mission_id"] = str(req.mission_id)
    try:
        generated_coas = coa_generator.generate(req.mission_type, facts)
        explanation = explanation_generator.generate(generated_coas, [])
    except Exception as e:
        logger.error("coa_generation_failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"Generation failed: {e}")

    coas = []
    for gen_coa in generated_coas:
        coa = COAResponse(
            id=uuid.UUID(gen_coa.id),
            mission_id=req.mission_id,
            coa_number=generated_coas.index(gen_coa) + 1,
            name=gen_coa.name,
            style=gen_coa.style,
            status="DRAFT",
            plan_graph=gen_coa.task_hierarchy,
            resource_plan=gen_coa.required_resources,
            timeline={"estimated_duration_min": gen_coa.estimated_duration_min},
            utility_score=gen_coa.utility_score,
            risk_adjusted_score=gen_coa.utility_score,  # Not explicitly in gen_coa but we can use utility
            explanation=ExplanationObject(
                decision=explanation.decision,
                primary_reasons=explanation.primary_reasons,
                supporting_evidence=[str(e) for e in explanation.supporting_evidence],
                rule_firings=gen_coa.validation.get("rule_firings", []),
                cbr_matches=gen_coa.cbr_matches,
                risk_factors=explanation.risk_factors,
                alternatives=[{"name": a["name"]} for a in explanation.alternatives],
                confidence=explanation.confidence,
                uncertainty_sources=explanation.uncertainty_sources,
                model_version=explanation.model_version
            ),
            created_at=datetime.now(timezone.utc)
        )
        coas.append(coa)
        
        if req.mission_id not in coa_store:
            coa_store[req.mission_id] = []
        coa_store[req.mission_id].append(coa)

    job_store[job_id] = {"status": "COMPLETED", "coas": coas}
    return {"job_id": job_id, "status": "COMPLETED"}

@app.get("/planning/jobs/{job_id}")
async def get_job_status(job_id: uuid.UUID):
    if job_id not in job_store:
        raise HTTPException(404, "Job not found")
    return {"job_id": job_id, **job_store[job_id]}

@app.get("/planning/missions/{mission_id}/coa")
async def list_coas(mission_id: uuid.UUID):
    return coa_store.get(mission_id, [])

@app.get("/planning/missions/{mission_id}/coa/{coa_id}")
async def get_coa(mission_id: uuid.UUID, coa_id: uuid.UUID):
    for coa in coa_store.get(mission_id, []):
        if coa.id == coa_id:
            return coa
    raise HTTPException(404, "COA not found")

@app.put("/planning/missions/{mission_id}/coa/{coa_id}")
async def modify_coa(mission_id: uuid.UUID, coa_id: uuid.UUID, modifications: dict):
    coa = await get_coa(mission_id, coa_id)
    # Apply modifications dynamically to the COA object
    for key, value in modifications.items():
        if hasattr(coa, key):
            setattr(coa, key, value)
    
    coa.status = "MODIFIED"
    return coa

@app.post("/planning/missions/{mission_id}/coa/{coa_id}/approve")
async def approve_coa(mission_id: uuid.UUID, coa_id: uuid.UUID, req: COAApprovalRequest):
    coa = await get_coa(mission_id, coa_id)
    coa.status = "APPROVED"
    return {"status": "APPROVED", "coa_id": coa_id}

@app.post("/planning/missions/{mission_id}/coa/{coa_id}/reject")
async def reject_coa(mission_id: uuid.UUID, coa_id: uuid.UUID, actor_id: uuid.UUID, reason: str):
    coa = await get_coa(mission_id, coa_id)
    coa.status = "REJECTED"
    return {"status": "REJECTED", "coa_id": coa_id}

@app.post("/planning/missions/{mission_id}/replan")
async def replan(mission_id: uuid.UUID, req: DynamicReplanRequest):
    return {"replan_id": uuid.uuid4(), "delta_plan": {}, "delta_explanation": "Replanned due to constraints."}

@app.post("/planning/cbr/retain")
async def retain_cbr_case(req: SimulationOutcome):
    if req.success_rate > 0.8:
        outcome = "SUCCESS"
    elif req.success_rate > 0.4:
        outcome = "PARTIAL"
    else:
        outcome = "FAILURE"
    
    lessons = [f"Vulnerability: {f['mode']}" for f in req.failure_modes if f.get('probability', 0) > 0.1]
    
    case = Case(
        id=f"SIM-{req.mission_id}-{req.coa_id}",
        mission_type=req.mission_type,
        terrain=req.terrain,
        threat=req.threat,
        resources=req.resources,
        urgency=req.urgency,
        outcome=outcome,
        plan_skeleton=req.plan_skeleton,
        lessons_learned=lessons
    )
    
    cbr.retain(case)
    cbr.save_index(CBR_DATA_PATH)
    
    return {"status": "RETAINED", "case_id": case.id}

@app.get("/planning/cbr/cases")
async def list_retained_cases():
    # Only return persisted real simulation cases
    sim_cases = [c for c in cbr.cases if c.id.startswith("SIM-")]
    return {"retained_count": len(sim_cases), "cases": [c.__dict__ for c in sim_cases]}
