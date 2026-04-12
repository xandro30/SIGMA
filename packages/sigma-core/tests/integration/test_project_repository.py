import pytest
from sigma_core.task_management.domain.entities.project import Project
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.domain.value_objects import ProjectId
from sigma_core.task_management.infrastructure.firestore.project_repository import FirestoreProjectRepository


@pytest.fixture
def area_id():
    return AreaId.generate()


@pytest.fixture
def project(area_id):
    return Project(
        id=ProjectId.generate(),
        name="GCP PCD",
        area_id=area_id,
        status=ProjectStatus.ACTIVE,
    )


@pytest.mark.asyncio
async def test_save_and_get_project(firestore_client, project):
    repo = FirestoreProjectRepository(firestore_client)

    await repo.save(project)
    result = await repo.get_by_id(project.id)

    assert result is not None
    assert result.id == project.id
    assert result.name == project.name
    assert result.status == ProjectStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_project_not_found(firestore_client):
    repo = FirestoreProjectRepository(firestore_client)

    result = await repo.get_by_id(ProjectId.generate())

    assert result is None


@pytest.mark.asyncio
async def test_delete_project(firestore_client, project):
    repo = FirestoreProjectRepository(firestore_client)
    await repo.save(project)

    await repo.delete(project.id)

    assert await repo.get_by_id(project.id) is None


@pytest.mark.asyncio
async def test_get_projects_by_area(firestore_client, area_id):
    repo = FirestoreProjectRepository(firestore_client)
    project1 = Project(id=ProjectId.generate(), name="P1", area_id=area_id, status=ProjectStatus.ACTIVE)
    project2 = Project(id=ProjectId.generate(), name="P2", area_id=area_id, status=ProjectStatus.ACTIVE)
    await repo.save(project1)
    await repo.save(project2)

    results = await repo.get_by_area(area_id)

    ids = [p.id for p in results]
    assert project1.id in ids
    assert project2.id in ids