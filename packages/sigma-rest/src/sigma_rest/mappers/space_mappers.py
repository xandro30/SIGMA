from sigma_core.task_management.domain.aggregates.space import Space
from sigma_rest.schemas.space_schemas import SpaceResponse, WorkflowStateResponse


def space_to_response(space: Space) -> SpaceResponse:
    return SpaceResponse(
        id=space.id.value,
        name=space.name.value,
        workflow_states=[
            WorkflowStateResponse(
                id=s.id.value,
                name=s.name,
                order=s.order,
            )
            for s in space.workflow_states
        ],
        transitions=[
            {"from_id": t.from_id.value, "to_id": t.to_id.value}
            for t in space.transitions
        ],
        created_at=space.created_at.value.isoformat(),
        updated_at=space.updated_at.value.isoformat(),
    )