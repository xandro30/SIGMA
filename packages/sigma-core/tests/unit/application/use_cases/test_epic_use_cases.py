import pytest
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.errors import (
    ProjectNotFoundError,
    EpicNotFoundError,
)
from sigma_core.shared_kernel.value_objects import AreaId, SpaceId
from sigma_core.task_management.domain.value_objects import ProjectId, EpicId
from sigma_core.task_management.application.use_cases.epic.create_epic import (
    CreateEpic, CreateEpicCommand,
)
from sigma_core.task_management.application.use_cases.epic.update_epic import (
    UpdateEpic, UpdateEpicCommand,
)
from sigma_core.task_management.application.use_cases.epic.delete_epic import (
    DeleteEpic, DeleteEpicCommand,
)
from tests.fakes.fake_epic_repository import FakeEpicRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_card_repository import FakeCardRepository


@pytest.fixture
def area_and_project():
    area = Area(id=AreaId.generate(), name="Work")
    project = Project(
        id=ProjectId.generate(),
        name="GCP PCD",
        area_id=area.id,
        status=ProjectStatus.ACTIVE,
    )
    return area, project


@pytest.mark.asyncio
async def test_create_epic(area_and_project):
    area, project = area_and_project
    epic_repo = FakeEpicRepository()
    project_repo = FakeProjectRepository()
    await project_repo.save(project)
    use_case = CreateEpic(epic_repo, project_repo)

    epic_id = await use_case.execute(CreateEpicCommand(
        space_id=SpaceId.generate(),
        project_id=project.id,
        name="Curso 1 — Cloud Fundamentals",
    ))

    epic = await epic_repo.get_by_id(epic_id)
    assert epic is not None
    assert epic.name == "Curso 1 — Cloud Fundamentals"
    assert epic.area_id == project.area_id


@pytest.mark.asyncio
async def test_create_epic_raises_error_if_project_not_found():
    epic_repo = FakeEpicRepository()
    project_repo = FakeProjectRepository()
    use_case = CreateEpic(epic_repo, project_repo)

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(CreateEpicCommand(
            space_id=SpaceId.generate(),
            project_id=ProjectId.generate(),
            name="Epic sin proyecto",
        ))


@pytest.mark.asyncio
async def test_update_epic_name(area_and_project):
    _, project = area_and_project
    epic_repo = FakeEpicRepository()
    epic = Epic(
        id=EpicId.generate(),
        space_id=SpaceId.generate(),
        project_id=project.id,
        area_id=project.area_id,
        name="Curso 1",
    )
    await epic_repo.save(epic)
    use_case = UpdateEpic(epic_repo)

    await use_case.execute(UpdateEpicCommand(
        epic_id=epic.id,
        name="Curso 1 — Cloud Fundamentals",
    ))

    updated = await epic_repo.get_by_id(epic.id)
    assert updated.name == "Curso 1 — Cloud Fundamentals"


@pytest.mark.asyncio
async def test_delete_epic(area_and_project):
    _, project = area_and_project
    epic_repo = FakeEpicRepository()
    card_repo = FakeCardRepository()
    epic = Epic(
        id=EpicId.generate(),
        space_id=SpaceId.generate(),
        project_id=project.id,
        area_id=project.area_id,
        name="Curso 1",
    )
    await epic_repo.save(epic)
    use_case = DeleteEpic(epic_repo, card_repo)

    await use_case.execute(DeleteEpicCommand(epic_id=epic.id))

    assert await epic_repo.get_by_id(epic.id) is None