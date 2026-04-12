import pytest
from sigma_core.task_management.domain.entities.epic import Epic
from sigma_core.shared_kernel.value_objects import SpaceId, AreaId
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.task_management.infrastructure.firestore.epic_repository import FirestoreEpicRepository


@pytest.fixture
def space_id():
    return SpaceId.generate()


@pytest.fixture
def project_id():
    return ProjectId.generate()


@pytest.fixture
def area_id():
    return AreaId.generate()


@pytest.fixture
def epic(space_id, project_id, area_id):
    return Epic(
        id=EpicId.generate(),
        space_id=space_id,
        project_id=project_id,
        area_id=area_id,
        name="Curso 1 — Cloud Fundamentals",
    )


@pytest.mark.asyncio
async def test_save_and_get_epic(firestore_client, epic):
    repo = FirestoreEpicRepository(firestore_client)

    await repo.save(epic)
    result = await repo.get_by_id(epic.id)

    assert result is not None
    assert result.id == epic.id
    assert result.name == epic.name


@pytest.mark.asyncio
async def test_get_epic_not_found(firestore_client):
    repo = FirestoreEpicRepository(firestore_client)

    result = await repo.get_by_id(EpicId.generate())

    assert result is None


@pytest.mark.asyncio
async def test_delete_epic(firestore_client, epic):
    repo = FirestoreEpicRepository(firestore_client)
    await repo.save(epic)

    await repo.delete(epic.id)

    assert await repo.get_by_id(epic.id) is None


@pytest.mark.asyncio
async def test_get_epics_by_space(firestore_client, space_id, project_id, area_id):
    repo = FirestoreEpicRepository(firestore_client)
    epic1 = Epic(id=EpicId.generate(), space_id=space_id, project_id=project_id, area_id=area_id, name="Epic 1")
    epic2 = Epic(id=EpicId.generate(), space_id=space_id, project_id=project_id, area_id=area_id, name="Epic 2")
    await repo.save(epic1)
    await repo.save(epic2)

    results = await repo.get_by_space(space_id)

    ids = [e.id for e in results]
    assert epic1.id in ids
    assert epic2.id in ids


@pytest.mark.asyncio
async def test_get_epics_by_project(firestore_client, space_id, project_id, area_id):
    repo = FirestoreEpicRepository(firestore_client)
    epic1 = Epic(id=EpicId.generate(), space_id=space_id, project_id=project_id, area_id=area_id, name="Epic 1")
    epic2 = Epic(id=EpicId.generate(), space_id=space_id, project_id=project_id, area_id=area_id, name="Epic 2")
    await repo.save(epic1)
    await repo.save(epic2)

    results = await repo.get_by_project(project_id)

    ids = [e.id for e in results]
    assert epic1.id in ids
    assert epic2.id in ids