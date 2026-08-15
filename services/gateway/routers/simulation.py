"""
Simulation Router — BATMAN Gateway (Phase 0 Skeleton)
Full implementation: Phase 1+
"""
from fastapi import APIRouter
router = APIRouter(prefix="/simulation")

@router.get("")
async def placeholder():
    return {"status": "not_implemented", "phase": "Phase 1+", "route": "/simulation"}
