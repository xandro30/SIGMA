from fastapi import APIRouter, Depends, Response

from sigma_core.task_management.domain.value_objects import SpaceId, EpicId, ProjectId
from sigma_core.task_management.application.use_cases.epic.create_epic import CreateEpic, CreateEpicCommand
from sigma_core.task_management.application.use_cases.epic.update_epic import UpdateEpic, UpdateEpicCommand
from sigma_core.task_management.application.use_cases.epic.delete_epic import DeleteEpic, DeleteEpicCommand

from sigma_rest.schemas.epic_schemas import CreateEpicRequest, UpdateEpicRequest
from sigma_rest.mappers.epic_mappers import epic_to_response
from sigma_rest.dependencies import get_epic_repo, get_project_repo, get_card_repo

router = APIRouter(tags=["epics"])


@router.get("/spaces/{space_id}/epics")
async def list_epics(space_id: str, epic_repo=Depends(get_epic_repo)):
    epics = await epic_repo.get_by_space(SpaceId(space_id))
    return {"epics": [epic_to_response(e) for e in epics]}


@router.post("/spaces/{space_id}/epics", status_code=201)
async def create_epic(
    space_id: str,
    body: CreateEpicRequest,
    epic_repo=Depends(get_epic_repo),
    project_repo=Depends(get_project_repo),
):
    use_case = CreateEpic(epic_repo, project_repo)
    epic_id = await use_case.execute(CreateEpicCommand(
        space_id=SpaceId(space_id),
        project_id=ProjectId(body.project_id),
        name=body.name,
        description=body.description,
    ))
    epic = await epic_repo.get_by_id(epic_id)
    return epic_to_response(epic)


@router.patch("/epics/{epic_id}")
async def update_epic(
    epic_id: str,
    body: UpdateEpicRequest,
    epic_repo=Depends(get_epic_repo),
):
    use_case = UpdateEpic(epic_repo)
    await use_case.execute(UpdateEpicCommand(
        epic_id=EpicId(epic_id),
        name=body.name,
        description=body.description,
    ))
    epic = await epic_repo.get_by_id(EpicId(epic_id))
    return epic_to_response(epic)


@router.delete("/epics/{epic_id}", status_code=204)
async def delete_epic(
    epic_id: str,
    epic_repo=Depends(get_epic_repo),
    card_repo=Depends(get_card_repo),
):
    use_case = DeleteEpic(epic_repo, card_repo)
    await use_case.execute(DeleteEpicCommand(epic_id=EpicId(epic_id)))
    return Response(status_code=204)