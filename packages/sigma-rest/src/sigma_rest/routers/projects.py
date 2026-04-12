from fastapi import APIRouter, Depends, Response

from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.domain.value_objects import ProjectId
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.application.use_cases.project.create_project import CreateProject, CreateProjectCommand
from sigma_core.task_management.application.use_cases.project.update_project import UpdateProject, UpdateProjectCommand
from sigma_core.task_management.application.use_cases.project.delete_project import DeleteProject, DeleteProjectCommand

from sigma_rest.schemas.project_schemas import CreateProjectRequest, UpdateProjectRequest
from sigma_rest.mappers.project_mappers import project_to_response
from sigma_rest.dependencies import get_project_repo, get_area_repo, get_card_repo

router = APIRouter(tags=["projects"])


@router.get("/areas/{area_id}/projects")
async def list_projects(area_id: str, project_repo=Depends(get_project_repo)):
    projects = await project_repo.get_by_area(AreaId(area_id))
    return {"projects": [project_to_response(p) for p in projects]}


@router.post("/areas/{area_id}/projects", status_code=201)
async def create_project(
    area_id: str,
    body: CreateProjectRequest,
    project_repo=Depends(get_project_repo),
    area_repo=Depends(get_area_repo),
):
    use_case = CreateProject(project_repo, area_repo)
    project_id = await use_case.execute(CreateProjectCommand(
        name=body.name,
        area_id=AreaId(area_id),
    ))
    project = await project_repo.get_by_id(project_id)
    return project_to_response(project)


@router.get("/projects/{project_id}")
async def get_project(project_id: str, project_repo=Depends(get_project_repo)):
    project = await project_repo.get_by_id(ProjectId(project_id))
    return project_to_response(project)


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: str,
    body: UpdateProjectRequest,
    project_repo=Depends(get_project_repo),
):
    use_case = UpdateProject(project_repo)
    await use_case.execute(UpdateProjectCommand(
        project_id=ProjectId(project_id),
        name=body.name,
        description=body.description,
        objectives=body.objectives,
        status=ProjectStatus(body.status) if body.status else None,
    ))
    project = await project_repo.get_by_id(ProjectId(project_id))
    return project_to_response(project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    project_repo=Depends(get_project_repo),
    card_repo=Depends(get_card_repo),
):
    use_case = DeleteProject(project_repo, card_repo)
    await use_case.execute(DeleteProjectCommand(project_id=ProjectId(project_id)))
    return Response(status_code=204)