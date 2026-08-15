from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.models.user import User
from app.db.database import get_db
from app.schemas.mission import MissionCreate, MissionResponse
from app.services.mission_service import (
    create_mission,
    get_mission,
    get_missions,
)


router = APIRouter(
    prefix="/missions",
    tags=["Missions"],
)


@router.post(
    "",
    response_model=MissionResponse,
    status_code=201,
)
def create(
    mission_data: MissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_mission(
        db,
        mission_data,
        current_user,
    )

@router.get(
    "",
    response_model=list[MissionResponse],
)
def list_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_missions(
        db,
        current_user,
    )

@router.get(
    "/{mission_id}",
    response_model=MissionResponse,
)
def get_by_id(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mission = get_mission(
        db,
        mission_id,
        current_user,
    )

    if mission is None:
        raise HTTPException(
            status_code=404,
            detail="Mission not found",
        )

    return mission