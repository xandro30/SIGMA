from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    objectives: str | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    objectives: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    objectives: str | None = None
    area_id: str
    status: str
    created_at: str
    updated_at: str