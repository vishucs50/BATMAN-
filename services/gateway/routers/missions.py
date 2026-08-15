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
