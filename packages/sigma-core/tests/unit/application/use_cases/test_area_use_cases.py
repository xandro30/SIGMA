import pytest
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.task_management.domain.errors import AreaNotFoundError
from sigma_core.shared_kernel.value_objects import AreaId
from sigma_core.task_management.application.use_cases.area.create_area import (
    CreateArea, CreateAreaCommand,
)
from sigma_core.task_management.application.use_cases.area.update_area import (
    UpdateArea, UpdateAreaCommand,
)
from sigma_core.task_management.application.use_cases.area.delete_area import (
    DeleteArea, DeleteAreaCommand,
)
from tests.fakes.fake_area_repository import FakeAreaRepository
from tests.fakes.fake_card_repository import FakeCardRepository
from tests.fakes.fake_project_repository import FakeProjectRepository


@pytest.mark.asyncio
async def test_create_area():
    area_repo = FakeAreaRepository()
    use_case = CreateArea(area_repo)

    area_id = await use_case.execute(CreateAreaCommand(name="Work"))

    area = await area_repo.get_by_id(area_id)
    assert area is not None
    assert area.name == "Work"


@pytest.mark.asyncio
async def test_update_area_name():
    area_repo = FakeAreaRepository()
    area = Area(id=AreaId.generate(), name="Work")
    await area_repo.save(area)
    use_case = UpdateArea(area_repo)

    await use_case.execute(UpdateAreaCommand(area_id=area.id, name="Personal"))

    updated = await area_repo.get_by_id(area.id)
    assert updated.name == "Personal"


@pytest.mark.asyncio
async def test_delete_area():
    area_repo = FakeAreaRepository()
    card_repo = FakeCardRepository()
    project_repo = FakeProjectRepository()
    area = Area(id=AreaId.generate(), name="Work")
    await area_repo.save(area)
    use_case = DeleteArea(area_repo, card_repo, project_repo)

    await use_case.execute(DeleteAreaCommand(area_id=area.id))

    assert await area_repo.get_by_id(area.id) is None


@pytest.mark.asyncio
async def test_update_area_raises_error_if_not_found():
    area_repo = FakeAreaRepository()
    use_case = UpdateArea(area_repo)

    with pytest.raises(AreaNotFoundError):
        await use_case.execute(UpdateAreaCommand(area_id=AreaId.generate(), name="X"))