"""
Missions Router — BATMAN Gateway
Proxies mission CRUD requests to batman-mission-svc.
"""
import uuid
from datetime import datetime
from typing import Optional

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ..config import Settings
from ..middleware.auth import RequireAnyStaff, RequireOpsOrAbove, TokenData

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/missions")
settings = Settings()


# ── SCHEMAS ───────────────────────────────────────────────────────────────────

class MissionCreate(BaseModel):
    mission_code: str
    mission_type: str
    classification: str = "UNCLASSIFIED"
    h_hour: Optional[datetime] = None
    mission_params: dict = {}
    roe_profile: dict = {}


class WhatIfRequest(BaseModel):
    mission_params: Optional[dict] = None
    roe_profile: Optional[dict] = None


class ObjectiveCreate(BaseModel):
    obj_type: str
    priority: int
    target_location: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None


class MissionSummary(BaseModel):
    id: uuid.UUID
    mission_code: str
    mission_type: str
    status: str
    classification: str
    created_at: datetime


# ── ENDPOINTS ─────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_mission(
    payload: MissionCreate,
    current_user: TokenData = Depends(RequireOpsOrAbove),
):
    """Create a new mission. Requires OPS_OFFICER or COMMANDING_OFFICER role."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                f"{settings.MISSION_SVC_URL}/missions",
                json=payload.model_dump(mode="json"),
                headers={"X-User-Id": current_user.user_id, "X-User-Role": current_user.roles[0] if current_user.roles else ""},
            )
            resp.raise_for_status()
            logger.info("mission_created", mission_code=payload.mission_code, user=current_user.username)
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.get("")
async def list_missions(
    status: Optional[str] = Query(None, description="Filter by mission status"),
    mission_type: Optional[str] = Query(None, description="Filter by mission type"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(RequireAnyStaff),
):
    """List all missions accessible to the current user."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            params = {"limit": limit, "offset": offset}
            if status:
                params["status"] = status
            if mission_type:
                params["mission_type"] = mission_type
            resp = await client.get(f"{settings.MISSION_SVC_URL}/missions", params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.get("/{mission_id}")
async def get_mission(
    mission_id: uuid.UUID,
    current_user: TokenData = Depends(RequireAnyStaff),
):
    """Get detailed mission information including objectives, constraints, and status."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{settings.MISSION_SVC_URL}/missions/{mission_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Mission not found")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.get("/{mission_id}/status")
async def get_mission_status(
    mission_id: uuid.UUID,
    current_user: TokenData = Depends(RequireAnyStaff),
):
    """Get live mission status — units, threats, alerts, phase progress."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{settings.MISSION_SVC_URL}/missions/{mission_id}/status")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.post("/{mission_id}/what-if", status_code=status.HTTP_201_CREATED)
async def create_what_if_branch(
    mission_id: uuid.UUID,
    payload: WhatIfRequest,
    current_user: TokenData = Depends(RequireOpsOrAbove),
):
    """Create a What-If branch of a mission and trigger COA generation."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Fetch original mission
            resp = await client.get(f"{settings.MISSION_SVC_URL}/missions/{mission_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Original mission not found")
            resp.raise_for_status()
            orig = resp.json()

            # 2. Prepare new mission payload
            new_params = dict(orig.get("mission_params", {}))
            if payload.mission_params:
                new_params.update(payload.mission_params)
                
            new_roe = dict(orig.get("roe_profile", {}))
            if payload.roe_profile:
                new_roe.update(payload.roe_profile)

            new_code = f"{orig.get('mission_code', 'MISSING')}-WHATIF"

            create_payload = {
                "mission_code": new_code,
                "mission_type": orig.get("mission_type"),
                "classification": orig.get("classification", "UNCLASSIFIED"),
                "mission_params": new_params,
                "roe_profile": new_roe
            }

            # 3. Create the cloned mission
            create_resp = await client.post(
                f"{settings.MISSION_SVC_URL}/missions",
                json=create_payload,
                headers={"X-User-Id": current_user.user_id, "X-User-Role": current_user.roles[0] if current_user.roles else ""}
            )
            create_resp.raise_for_status()
            new_mission = create_resp.json()
            new_mission_id = new_mission["id"]

            # 4. Trigger COA Generation for the new mission
            plan_payload = {
                "mission_id": str(new_mission_id),
                "mission_type": new_mission.get("mission_type", "COUNTER_INFILTRATION"),
                "styles": ["BOLD", "BALANCED", "CAUTIOUS"],
                "world_state": new_mission.get("mission_params", {})
            }
            plan_resp = await client.post(f"{settings.PLANNING_SVC_URL}/planning/coa/generate", json=plan_payload)
            plan_resp.raise_for_status()

            logger.info("what_if_branch_created", orig_mission=str(mission_id), new_mission=new_mission_id)
            return new_mission

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service unavailable")


@router.post("/{mission_id}/objectives", status_code=status.HTTP_201_CREATED)
async def create_objective(
    mission_id: uuid.UUID,
    payload: ObjectiveCreate,
    current_user: TokenData = Depends(RequireOpsOrAbove),
):
    """Create a new objective for a mission."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(
                f"{settings.MISSION_SVC_URL}/missions/{mission_id}/objectives",
                json=payload.model_dump(mode="json"),
                headers={"X-User-Id": current_user.user_id, "X-User-Role": current_user.roles[0] if current_user.roles else ""},
            )
            resp.raise_for_status()
            logger.info("objective_created", mission_id=str(mission_id), user=current_user.username)
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.get("/{mission_id}/objectives")
async def list_objectives(
    mission_id: uuid.UUID,
    current_user: TokenData = Depends(RequireAnyStaff),
):
    """List all objectives for a mission."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{settings.MISSION_SVC_URL}/missions/{mission_id}/objectives")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")


@router.get("/objectives/{objective_id}")
async def get_objective(
    objective_id: uuid.UUID,
    current_user: TokenData = Depends(RequireAnyStaff),
):
    """Get detailed objective information."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{settings.MISSION_SVC_URL}/objectives/{objective_id}")
            if resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Objective not found")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Mission service unavailable")

# --- COA Proxy Endpoints ---

@router.post("/{mission_id}/coas/generate")
async def generate_coa_for_mission(mission_id: uuid.UUID, current_user: TokenData = Depends(RequireAnyStaff)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Fetch mission to get real mission type
            mission_resp = await client.get(f"{settings.MISSION_SVC_URL}/missions/{mission_id}")
            if mission_resp.status_code == 404:
                raise HTTPException(status_code=404, detail="Mission not found")
            mission_resp.raise_for_status()
            mission_data = mission_resp.json()
            
            payload = {
                "mission_id": str(mission_id),
                "mission_type": mission_data.get("mission_type", "COUNTER_INFILTRATION"),
                "styles": ["BOLD", "BALANCED", "CAUTIOUS"],
                "world_state": mission_data.get("mission_params", {})
            }
            
            resp = await client.post(f"{settings.PLANNING_SVC_URL}/planning/coa/generate", json=payload)
            resp.raise_for_status()
            
            # Fetch and return the newly generated COAs
            coas_resp = await client.get(f"{settings.PLANNING_SVC_URL}/planning/missions/{mission_id}/coa")
            return coas_resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Service unavailable")

@router.get("/{mission_id}/coas")
async def get_mission_coas(mission_id: uuid.UUID, current_user: TokenData = Depends(RequireAnyStaff)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(f"{settings.PLANNING_SVC_URL}/planning/missions/{mission_id}/coa")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Planning service unavailable")

@router.post("/{mission_id}/coas/{coa_id}/approve")
async def approve_mission_coa(mission_id: uuid.UUID, coa_id: uuid.UUID, current_user: TokenData = Depends(RequireAnyStaff)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        payload = {
            "actor_id": current_user.user_id,
            "actor_role": current_user.roles[0] if current_user.roles else "STAFF",
            "rationale": "Approved via UI"
        }
        try:
            resp = await client.post(f"{settings.PLANNING_SVC_URL}/planning/missions/{mission_id}/coa/{coa_id}/approve", json=payload)
            resp.raise_for_status()
            # return the updated COA
            coa_resp = await client.get(f"{settings.PLANNING_SVC_URL}/planning/missions/{mission_id}/coa/{coa_id}")
            return coa_resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Planning service unavailable")

@router.post("/{mission_id}/coas/{coa_id}/simulate")
async def simulate_mission_coa(mission_id: uuid.UUID, coa_id: uuid.UUID, current_user: TokenData = Depends(RequireAnyStaff)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        payload = {
            "mission_id": str(mission_id),
            "coa_id": str(coa_id),
            "coa_data": {},
            "mc_runs": 50,
            "parallel_workers": 4
        }
        try:
            resp = await client.post(f"{settings.WARGAME_SVC_URL}/wargame/simulate", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Wargame service unavailable")
