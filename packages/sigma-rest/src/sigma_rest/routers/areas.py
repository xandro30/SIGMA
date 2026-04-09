from fastapi import APIRouter, Depends, Response

from sigma_core.task_management.domain.value_objects import AreaId
from sigma_core.task_management.application.use_cases.area.create_area import CreateArea, CreateAreaCommand
from sigma_core.task_management.application.use_cases.area.update_area import UpdateArea, UpdateAreaCommand
from sigma_core.task_management.application.use_cases.area.delete_area import DeleteArea, DeleteAreaCommand
from sigma_core.task_management.application.use_cases.epic.get_epics_by_area import GetEpicsByArea, GetEpicsByAreaQuery

from sigma_rest.schemas.area_schemas import CreateAreaRequest, UpdateAreaRequest
from sigma_rest.mappers.area_mappers import area_to_response
from sigma_rest.mappers.epic_mappers import epic_to_response
from sigma_rest.dependencies import get_area_repo, get_card_repo, get_project_repo, get_epic_repo

router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("")
async def list_areas(area_repo=Depends(get_area_repo)):
    areas = await area_repo.get_all()
    return {"areas": [area_to_response(a) for a in areas]}


@router.post("", status_code=201)
async def create_area(
    body: CreateAreaRequest,
    area_repo=Depends(get_area_repo),
):
    use_case = CreateArea(area_repo)
    area_id = await use_case.execute(CreateAreaCommand(name=body.name, color_id=body.color_id))
    area = await area_repo.get_by_id(area_id)
    return area_to_response(area)


@router.patch("/{area_id}")
async def update_area(
    area_id: str,
    body: UpdateAreaRequest,
    area_repo=Depends(get_area_repo),
):
    use_case = UpdateArea(area_repo)
    await use_case.execute(UpdateAreaCommand(
        area_id=AreaId(area_id),
        name=body.name,
        description=body.description,
        objectives=body.objectives,
        color_id=body.color_id,
    ))
    area = await area_repo.get_by_id(AreaId(area_id))
    return area_to_response(area)


@router.get("/{area_id}/epics")
async def list_epics_by_area(
    area_id: str,
    project_repo=Depends(get_project_repo),
    epic_repo=Depends(get_epic_repo),
):
    use_case = GetEpicsByArea(project_repo, epic_repo)
    epics = await use_case.execute(GetEpicsByAreaQuery(area_id=AreaId(area_id)))
    return {"epics": [epic_to_response(e) for e in epics]}


@router.delete("/{area_id}", status_code=204)
async def delete_area(
    area_id: str,
    area_repo=Depends(get_area_repo),
    card_repo=Depends(get_card_repo),
    project_repo=Depends(get_project_repo),
):
    use_case = DeleteArea(area_repo, card_repo, project_repo)
    await use_case.execute(DeleteAreaCommand(area_id=AreaId(area_id)))
    return Response(status_code=204)