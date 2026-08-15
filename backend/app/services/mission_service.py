from sqlalchemy.orm import Session

from app.models.mission import Mission
from app.models.user import User
from app.schemas.mission import MissionCreate


def create_mission(
    db: Session,
    mission_data: MissionCreate,
    current_user: User,
) -> Mission:
    mission = Mission(
        mission_code=mission_data.mission_code,
        mission_type=mission_data.mission_type,
        description=mission_data.description,
        created_by=current_user.id,
    )

    db.add(mission)
    db.commit()
    db.refresh(mission)

    return mission


def get_missions(
    db: Session,
    current_user: User,
) -> list[Mission]:
    return (
        db.query(Mission)
        .filter(Mission.created_by == current_user.id)
        .all()
    )


def get_mission(
    db: Session,
    mission_id: int,
    current_user: User,
) -> Mission | None:
    return (
        db.query(Mission)
        .filter(
            Mission.id == mission_id,
            Mission.created_by == current_user.id,
        )
        .first()
    )   