import pytest
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.errors import AreaNotFoundError, ProjectNotFoundError
from sigma_core.task_management.domain.value_objects import AreaId, ProjectId
from sigma_core.task_management.application.use_cases.project.create_project import (
    CreateProject, CreateProjectCommand,
)
from sigma_core.task_management.application.use_cases.project.update_project import (
    UpdateProject, UpdateProjectCommand,
)
from sigma_core.task_management.application.use_cases.project.delete_project import (
    DeleteProject, DeleteProjectCommand,
)
from tests.fakes.fake_area_repository import FakeAreaRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_card_repository import FakeCardRepository


@pytest.mark.asyncio
async def test_create_project():
    area_repo = FakeAreaRepository()
    project_repo = FakeProjectRepository()
    area = Area(id=AreaId.generate(), name="Work")
    await area_repo.save(area)
    use_case = CreateProject(project_repo, area_repo)

    project_id = await use_case.execute(CreateProjectCommand(
        name="GCP PCD",
        area_id=area.id,
    ))

    project = await project_repo.get_by_id(project_id)
    assert project is not None
    assert project.name == "GCP PCD"
    assert project.area_id == area.id
    assert project.status == ProjectStatus.ACTIVE


@pytest.mark.asyncio
async def test_create_project_raises_error_if_area_not_found():
    area_repo = FakeAreaRepository()
    project_repo = FakeProjectRepository()
    use_case = CreateProject(project_repo, area_repo)

    with pytest.raises(AreaNotFoundError):
        await use_case.execute(CreateProjectCommand(
            name="GCP PCD",
            area_id=AreaId.generate(),
        ))


@pytest.mark.asyncio
async def test_update_project_status():
    project_repo = FakeProjectRepository()
    project = Project(
        id=ProjectId.generate(),
        name="GCP PCD",
        area_id=AreaId.generate(),
        status=ProjectStatus.ACTIVE,
    )
    await project_repo.save(project)
    use_case = UpdateProject(project_repo)

    await use_case.execute(UpdateProjectCommand(
        project_id=project.id,
        status=ProjectStatus.COMPLETED,
    ))

    updated = await project_repo.get_by_id(project.id)
    assert updated.status == ProjectStatus.COMPLETED


@pytest.mark.asyncio
async def test_delete_project():
    project_repo = FakeProjectRepository()
    card_repo = FakeCardRepository()
    project = Project(
        id=ProjectId.generate(),
        name="GCP PCD",
        area_id=AreaId.generate(),
        status=ProjectStatus.ACTIVE,
    )
    await project_repo.save(project)
    use_case = DeleteProject(project_repo, card_repo)

    await use_case.execute(DeleteProjectCommand(project_id=project.id))

    assert await project_repo.get_by_id(project.id) is None