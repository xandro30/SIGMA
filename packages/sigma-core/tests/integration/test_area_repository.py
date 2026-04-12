import pytest
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.infrastructure.firestore.area_repository import FirestoreAreaRepository


@pytest.fixture
def area():
    return Area(id=AreaId.generate(), name="Work")


@pytest.mark.asyncio
async def test_save_and_get_area(firestore_client, area):
    repo = FirestoreAreaRepository(firestore_client)

    await repo.save(area)
    result = await repo.get_by_id(area.id)

    assert result is not None
    assert result.id == area.id
    assert result.name == area.name


@pytest.mark.asyncio
async def test_get_area_not_found(firestore_client):
    repo = FirestoreAreaRepository(firestore_client)

    result = await repo.get_by_id(AreaId.generate())

    assert result is None


@pytest.mark.asyncio
async def test_delete_area(firestore_client, area):
    repo = FirestoreAreaRepository(firestore_client)
    await repo.save(area)

    await repo.delete(area.id)

    assert await repo.get_by_id(area.id) is None


@pytest.mark.asyncio
async def test_get_all_areas(firestore_client):
    repo = FirestoreAreaRepository(firestore_client)
    area1 = Area(id=AreaId.generate(), name="Work")
    area2 = Area(id=AreaId.generate(), name="Personal")
    await repo.save(area1)
    await repo.save(area2)

    results = await repo.get_all()

    ids = [a.id for a in results]
    assert area1.id in ids
    assert area2.id in ids