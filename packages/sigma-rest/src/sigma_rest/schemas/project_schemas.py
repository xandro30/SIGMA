from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    objectives: list[str] = []


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    objectives: list[str] = []
    area_id: str
    status: str
    created_at: str
    updated_at: str