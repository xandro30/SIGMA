from pydantic import BaseModel


class CreateAreaRequest(BaseModel):
    name: str
    description: str | None = None
    objectives: str | None = None
    color_id: str | None = None


class UpdateAreaRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    objectives: str | None = None
    color_id: str | None = None


class AreaResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    objectives: str | None = None
    color_id: str | None = None
    created_at: str
    updated_at: str