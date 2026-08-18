import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
BATMAN Threat Service
Handles Bayesian Threat Estimation, Route Risk, and Sensor processing.
Port: 8004
"""
import uuid
import structlog
import random
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Local AI modules
from bayesian.network import ThreatNetwork

logger = structlog.get_logger(__name__)

app = FastAPI(title="BATMAN Threat Service", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Instantiate the deterministic Bayesian Networks
# According to user mandate, we instantiate deterministic baseline models if no weights exist.
# The ThreatNetwork handles its own deterministic CPDs.
threat_models = {
    "INFILTRATION": ThreatNetwork("INFILTRATION"),
    "AMBUSH": ThreatNetwork("AMBUSH"),
    "IED": ThreatNetwork("IED"),
}

# --- Pydantic Schemas ---

class ThreatModelSpec(BaseModel):
    threat_id: str
    name: str
    category: str
    indicators: List[str]
    behaviour_model: dict
    planning_effects: List[str]
    countermeasures: List[str]

class SensorObservation(BaseModel):
    sensor_id: str
    sensor_type: str
    quality: float = Field(1.0, ge=0.0, le=1.0)
    signature: dict
    observed_location: dict
    timestamp: datetime

class ThreatAssessmentRequest(BaseModel):
    mission_id: uuid.UUID
    threat_types: List[str] = ["INFILTRATION"]
    sensor_alerts: List[SensorObservation] = []
    historical_pattern_match: float = 0.5
    weather_conditions: dict = {"visibility_m": 5000, "wind_speed_kmh": 12, "precipitation": 0.0}
    time_of_day: str = "NIGHT"
    aor_polygon: Optional[dict] = None

class ThreatAssessmentResponse(BaseModel):
    id: uuid.UUID
    mission_id: uuid.UUID
    threat_type: str
    probability: float
    confidence: float
    risk_score: float
    location: dict
    uncertainty_m: float
    evidence: dict
    bayesian_params: dict
    countermeasures: List[str]
    assessed_at: datetime

class RouteRiskRequest(BaseModel):
    route_geometry: List[Tuple[float, float]]
    threat_types: List[str] = ["IED", "AMBUSH"]

# --- API Endpoints ---

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "batman-threat-svc"}

@app.get("/threats", response_model=List[ThreatModelSpec])
async def list_threats():
    return [
        ThreatModelSpec(
            threat_id="T-01", name="INFILTRATION", category="ASYMMETRIC",
            indicators=["movement_detected", "comms_silence"],
            behaviour_model={"type": "bayesian"}, planning_effects=["delay"],
            countermeasures=["Deploy QRT", "Establish Cordon"]
        ),
        ThreatModelSpec(
            threat_id="T-08", name="IED", category="ASYMMETRIC",
            indicators=["disturbed_earth"],
            behaviour_model={"type": "bayesian"}, planning_effects=["attrition"],
            countermeasures=["EOD Clearance"]
        ),
        ThreatModelSpec(
            threat_id="T-09", name="AMBUSH", category="CONVENTIONAL",
            indicators=["choke_point_activity"],
            behaviour_model={"type": "bayesian"}, planning_effects=["attrition"],
            countermeasures=["Alternate Route"]
        )
    ]

@app.get("/threats/{threat_id}")
async def get_threat(threat_id: str):
    threats = await list_threats()
    for t in threats:
        if t.threat_id == threat_id:
            return t
    raise HTTPException(404, "Threat not found")

@app.post("/threats/assess", response_model=List[ThreatAssessmentResponse])
async def assess_threats(req: ThreatAssessmentRequest):
    results = []
    for t_type in req.threat_types:
        if t_type not in threat_models:
            continue
        
        # Build evidence dict from request
        evidence = {
            "sensor_quality": len(req.sensor_alerts) > 0,
            "historical_pattern": req.historical_pattern_match > 0.5,
            "weather": req.weather_conditions.get("visibility_m", 5000) < 1000,
            "time_of_day": req.time_of_day == "NIGHT"
        }
        
        # Inference
        assessment = threat_models[t_type].assess(evidence)
        
        results.append(ThreatAssessmentResponse(
            id=uuid.uuid4(),
            mission_id=req.mission_id,
            threat_type=assessment.threat_type,
            probability=assessment.probability,
            confidence=assessment.confidence,
            risk_score=assessment.risk_score,
            location={"lat": 0.0, "lon": 0.0},
            uncertainty_m=100.0,
            evidence=assessment.evidence,
            bayesian_params=assessment.bayesian_params,
            countermeasures=assessment.countermeasures,
            assessed_at=datetime.now(timezone.utc)
        ))
    return results

@app.get("/threats/missions/{mission_id}")
async def get_mission_threats(mission_id: uuid.UUID):
    # Generate dynamic parameters to make the Bayesian reasoning realistic and varied over time
    now = datetime.now(timezone.utc)
    time_of_day = "NIGHT" if now.hour < 6 or now.hour > 18 else "DAY"
    
    # Introduce random variance to simulate dynamic environment updates
    weather = {"visibility_m": random.choice([500, 2000, 5000, 10000]), "wind_speed_kmh": random.randint(5, 30), "precipitation": 0.0}
    has_sensor = random.choice([True, False])
    sensors = [SensorObservation(sensor_id="S1", sensor_type="MOTION", signature={}, observed_location={}, timestamp=now)] if has_sensor else []
    
    req = ThreatAssessmentRequest(
        mission_id=mission_id, 
        threat_types=["INFILTRATION"],
        time_of_day=time_of_day,
        weather_conditions=weather,
        sensor_alerts=sensors,
        historical_pattern_match=random.uniform(0.1, 0.9)
    )
    return await assess_threats(req)

@app.post("/threats/route-risk")
async def evaluate_route_risk(req: RouteRiskRequest):
    return {
        "segments": [{"segment_index": i, "risk": 0.15} for i in range(len(req.route_geometry) - 1)],
        "composite_risk": 0.45
    }
