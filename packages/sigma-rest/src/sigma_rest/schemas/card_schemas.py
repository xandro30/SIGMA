from typing import Literal

from pydantic import BaseModel, Field


class CreateCardRequest(BaseModel):
    title: str
    initial_stage: str = "inbox"
    description: str | None = None
    priority: str | None = None
    area_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    due_date: str | None = None
    labels: list[str] = []
    topics: list[str] = []


class UpdateCardRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    due_date: str | None = None
    # None = no enviado (no tocar); str vacío o ausencia → limpiar con null explícito
    area_id: str | None = None
    epic_id: str | None = None
    labels: list[str] | None = None


class MoveCardRequest(BaseModel):
    target_state_id: str


class PromoteCardRequest(BaseModel):
    target_state_id: str | None = None


class DemoteCardRequest(BaseModel):
    stage: str = "backlog"


class MoveTriageStageRequest(BaseModel):
    stage: str  # "inbox" | "refinement" | "backlog"


class LabelActionRequest(BaseModel):
    action: str  # "add" | "remove"
    label: str


class TopicActionRequest(BaseModel):
    action: str
    topic: str


class UrlActionRequest(BaseModel):
    action: str
    url: str


class AddChecklistItemRequest(BaseModel):
    text: str


class AddRelatedCardRequest(BaseModel):
    related_card_id: str


class AssignAreaRequest(BaseModel):
    area_id: str | None


class AssignProjectRequest(BaseModel):
    project_id: str | None


class AssignEpicRequest(BaseModel):
    epic_id: str | None


class AssignSizeRequest(BaseModel):
    size: Literal["xxs", "xs", "s", "m", "l", "xl", "xxl"] | None


class StartTimerRequest(BaseModel):
    description: str = ""


class AddWorkLogRequest(BaseModel):
    description: str
    minutes: int = Field(gt=0)


class ChecklistItemResponse(BaseModel):
    text: str
    done: bool


class CardResponse(BaseModel):
    id: str
    space_id: str
    title: str
    description: str | None = None
    pre_workflow_stage: str | None = None
    workflow_state_id: str | None = None
    area_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    priority: str | None = None
    labels: list[str] = []
    topics: list[str] = []
    urls: list[str] = []
    checklist: list[ChecklistItemResponse] = []
    related_cards: list[str] = []
    due_date: str | None = None
    size: str | None = None
    actual_time: int
    timer_started_at: str | None = None
    created_at: str
    updated_at: str