from pydantic import BaseModel


class CreateEpicRequest(BaseModel):
    name: str
    project_id: str
    description: str | None = None


class UpdateEpicRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class EpicResponse(BaseModel):
    id: str
    space_id: str
    project_id: str
    area_id: str
    name: str
    description: str | None = None
    created_at: str
    updated_at: str