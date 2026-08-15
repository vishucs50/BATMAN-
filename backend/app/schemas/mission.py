from uuid import UUID

from pydantic import BaseModel


class MissionCreate(BaseModel):
    mission_code: str
    mission_type: str
    description: str | None = None


class MissionResponse(BaseModel):
    id: int
    mission_code: str
    mission_type: str
    description: str | None
    status: str
    created_by: UUID | None

    model_config = {
        "from_attributes": True
    }