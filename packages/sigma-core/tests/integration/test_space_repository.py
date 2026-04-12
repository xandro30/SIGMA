import pytest
from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.task_management.domain.value_objects import SpaceName
from sigma_core.task_management.infrastructure.firestore.space_repository import (
    FirestoreSpaceRepository,
)


@pytest.mark.asyncio
async def test_save_and_get_space(firestore_client):
    repo = FirestoreSpaceRepository(firestore_client)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))

    await repo.save(space)
    result = await repo.get_by_id(space.id)

    assert result is not None
    assert result.id == space.id
    assert result.name == space.name


@pytest.mark.asyncio
async def test_get_space_not_found(firestore_client):
    repo = FirestoreSpaceRepository(firestore_client)

    result = await repo.get_by_id(SpaceId.generate())

    assert result is None


@pytest.mark.asyncio
async def test_delete_space(firestore_client):
    repo = FirestoreSpaceRepository(firestore_client)
    space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
    await repo.save(space)

    await repo.delete(space.id)

    assert await repo.get_by_id(space.id) is None