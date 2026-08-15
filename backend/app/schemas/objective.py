from datetime import datetime

from pydantic import BaseModel


class ObjectiveCreate(BaseModel):
    obj_type: str
    priority: int
    target_location: str | None = None
    deadline: datetime | None = None
    description: str | None = None


class ObjectiveResponse(BaseModel):
    id: int
    mission_id: int
    obj_type: str
    priority: int
    target_location: str | None
    deadline: datetime | None
    status: str
    description: str | None

    model_config = {
        "from_attributes": True
    }