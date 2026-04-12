from pydantic import BaseModel, Field, NonNegativeInt


class CreateSpaceRequest(BaseModel):
    name: str


class AddWorkflowStateRequest(BaseModel):
    name: str
    order: int


class AddTransitionRequest(BaseModel):
    from_id: str
    to_id: str


class SetSizeMappingRequest(BaseModel):
    # dict[str, NonNegativeInt] con keys xxs..xxl (máx 7) | None para limpiar
    mapping: dict[str, NonNegativeInt] | None = Field(default=None, max_length=7)


class WorkflowStateResponse(BaseModel):
    id: str
    name: str
    order: int


class SpaceResponse(BaseModel):
    id: str
    name: str
    workflow_states: list[WorkflowStateResponse]
    transitions: list[dict]
    size_mapping: dict[str, int] | None = None
    created_at: str
    updated_at: str