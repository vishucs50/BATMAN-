from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.objective import ObjectiveCreate, ObjectiveResponse
from app.services.objective_service import (
    create_objective,
    get_objective,
    get_objectives_for_mission,
)


router = APIRouter(
    prefix="/missions",
    tags=["Objectives"],
)


@router.post(
    "/{mission_id}/objectives",
    response_model=ObjectiveResponse,
    status_code=201,
)
def create(
    mission_id: int,
    objective_data: ObjectiveCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_objective(
            db,
            mission_id,
            objective_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/{mission_id}/objectives",
    response_model=list[ObjectiveResponse],
)
def list_for_mission(
    mission_id: int,
    db: Session = Depends(get_db),
):
    return get_objectives_for_mission(
        db,
        mission_id,
    )


@router.get(
    "/objectives/{objective_id}",
    response_model=ObjectiveResponse,
)
def get_by_id(
    objective_id: int,
    db: Session = Depends(get_db),
):
    objective = get_objective(
        db,
        objective_id,
    )

    if objective is None:
        raise HTTPException(
            status_code=404,
            detail="Objective not found",
        )

    return objective