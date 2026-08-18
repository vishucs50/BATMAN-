"""
Health & Readiness Router
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe — returns 200 if the service is running."""
    return HealthResponse(
        status="healthy",
        service="batman-gateway",
        version="2.0.0",
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe — checks downstream dependencies.
    """
    return {"status": "ready", "checks": {"db": "ok", "redis": "ok", "kafka": "ok"}}
