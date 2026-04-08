from pydantic import BaseModel


class CreateSpaceRequest(BaseModel):
    name: str


class AddWorkflowStateRequest(BaseModel):
    name: str
    order: int


class AddTransitionRequest(BaseModel):
    from_id: str
    to_id: str


class WorkflowStateResponse(BaseModel):
    id: str
    name: str
    order: int


class SpaceResponse(BaseModel):
    id: str
    name: str
    workflow_states: list[WorkflowStateResponse]
    transitions: list[dict]
    created_at: str
    updated_at: str