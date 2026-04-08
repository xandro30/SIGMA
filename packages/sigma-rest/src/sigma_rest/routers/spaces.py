from fastapi import APIRouter, Depends, Response

from sigma_core.task_management.domain.value_objects import SpaceId, SpaceName, WorkflowStateId
from sigma_core.task_management.application.use_cases.space.create_space import CreateSpace, CreateSpaceCommand
from sigma_core.task_management.application.use_cases.space.add_workflow_state import AddWorkflowState, AddWorkflowStateCommand
from sigma_core.task_management.application.use_cases.space.remove_workflow_state import RemoveWorkflowState, RemoveWorkflowStateCommand
from sigma_core.task_management.application.use_cases.space.add_transition import AddTransition, AddTransitionCommand

from sigma_rest.schemas.space_schemas import CreateSpaceRequest, AddWorkflowStateRequest, AddTransitionRequest, SpaceResponse
from sigma_rest.mappers.space_mappers import space_to_response
from sigma_rest.dependencies import get_space_repo

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("")
async def list_spaces(space_repo=Depends(get_space_repo)):
    spaces = await space_repo.get_all()
    return {"spaces": [space_to_response(s) for s in spaces]}


@router.post("", status_code=201)
async def create_space(
    body: CreateSpaceRequest,
    space_repo=Depends(get_space_repo),
):
    use_case = CreateSpace(space_repo)
    space_id = await use_case.execute(CreateSpaceCommand(name=SpaceName(body.name)))
    space = await space_repo.get_by_id(space_id)
    return space_to_response(space)


@router.get("/{space_id}")
async def get_space(space_id: str, space_repo=Depends(get_space_repo)):
    space = await space_repo.get_by_id(SpaceId(space_id))
    return space_to_response(space)


@router.delete("/{space_id}", status_code=204)
async def delete_space(space_id: str, space_repo=Depends(get_space_repo)):
    await space_repo.delete(SpaceId(space_id))
    return Response(status_code=204)


@router.post("/{space_id}/workflow-states", status_code=201)
async def add_workflow_state(
    space_id: str,
    body: AddWorkflowStateRequest,
    space_repo=Depends(get_space_repo),
):
    use_case = AddWorkflowState(space_repo)
    await use_case.execute(AddWorkflowStateCommand(
        space_id=SpaceId(space_id),
        name=body.name,
        order=body.order,
    ))
    space = await space_repo.get_by_id(SpaceId(space_id))
    return space_to_response(space)


@router.delete("/{space_id}/workflow-states/{state_id}", status_code=200)
async def remove_workflow_state(
    space_id: str,
    state_id: str,
    space_repo=Depends(get_space_repo),
):
    use_case = RemoveWorkflowState(space_repo)
    await use_case.execute(RemoveWorkflowStateCommand(
        space_id=SpaceId(space_id),
        state_id=WorkflowStateId(state_id),
    ))
    space = await space_repo.get_by_id(SpaceId(space_id))
    return space_to_response(space)


@router.post("/{space_id}/transitions", status_code=201)
async def add_transition(
    space_id: str,
    body: AddTransitionRequest,
    space_repo=Depends(get_space_repo),
):
    use_case = AddTransition(space_repo)
    await use_case.execute(AddTransitionCommand(
        space_id=SpaceId(space_id),
        from_id=WorkflowStateId(body.from_id),
        to_id=WorkflowStateId(body.to_id),
    ))
    space = await space_repo.get_by_id(SpaceId(space_id))
    return space_to_response(space)