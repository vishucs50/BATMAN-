from sqlalchemy.orm import Session

from app.models.mission import Mission
from app.models.objective import Objective
from app.schemas.objective import ObjectiveCreate


def create_objective(
    db: Session,
    mission_id: int,
    objective_data: ObjectiveCreate,
) -> Objective:
    mission = (
        db.query(Mission)
        .filter(Mission.id == mission_id)
        .first()
    )

    if mission is None:
        raise ValueError("Mission not found")

    objective = Objective(
        mission_id=mission_id,
        obj_type=objective_data.obj_type,
        priority=objective_data.priority,
        target_location=objective_data.target_location,
        deadline=objective_data.deadline,
        description=objective_data.description,
    )

    db.add(objective)
    db.commit()
    db.refresh(objective)

    return objective


def get_objectives_for_mission(
    db: Session,
    mission_id: int,
) -> list[Objective]:
    return (
        db.query(Objective)
        .filter(Objective.mission_id == mission_id)
        .all()
    )


def get_objective(
    db: Session,
    objective_id: int,
) -> Objective | None:
    return (
        db.query(Objective)
        .filter(Objective.id == objective_id)
        .first()
    )