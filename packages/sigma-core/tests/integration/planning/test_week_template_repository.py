import pytest

from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.value_objects import (
    DayTemplateId,
    WeekTemplateId,
)
from sigma_core.planning.infrastructure.firestore.week_template_repository import (
    FirestoreWeekTemplateRepository,
)
from sigma_core.shared_kernel.value_objects import SpaceId


def _week(
    space_id: SpaceId,
    *,
    name: str = "Semana estándar",
    slots: dict[DayOfWeek, DayTemplateId | None] | None = None,
) -> WeekTemplate:
    return WeekTemplate(
        id=WeekTemplateId.generate(),
        space_id=space_id,
        name=name,
        slots=dict(slots or {}),
    )


@pytest.mark.asyncio
async def test_save_and_get_week_template(firestore_client):
    repo = FirestoreWeekTemplateRepository(firestore_client)
    dt_mon = DayTemplateId.generate()
    dt_wed = DayTemplateId.generate()
    tpl = _week(
        SpaceId.generate(),
        slots={DayOfWeek.MONDAY: dt_mon, DayOfWeek.WEDNESDAY: dt_wed},
    )

    await repo.save(tpl)
    result = await repo.get_by_id(tpl.id)

    assert result is not None
    assert result.id == tpl.id
    assert result.slots[DayOfWeek.MONDAY] == dt_mon
    assert result.slots[DayOfWeek.WEDNESDAY] == dt_wed
    assert result.slots[DayOfWeek.TUESDAY] is None
    assert result.slots[DayOfWeek.SUNDAY] is None


@pytest.mark.asyncio
async def test_get_week_template_not_found(firestore_client):
    repo = FirestoreWeekTemplateRepository(firestore_client)
    assert await repo.get_by_id(WeekTemplateId.generate()) is None


@pytest.mark.asyncio
async def test_list_by_space(firestore_client):
    repo = FirestoreWeekTemplateRepository(firestore_client)
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()

    await repo.save(_week(space_a, name="A1"))
    await repo.save(_week(space_a, name="A2"))
    await repo.save(_week(space_b, name="B1"))

    result = await repo.list_by_space(space_a)
    assert {t.name for t in result} == {"A1", "A2"}


@pytest.mark.asyncio
async def test_delete_week_template(firestore_client):
    repo = FirestoreWeekTemplateRepository(firestore_client)
    tpl = _week(SpaceId.generate())
    await repo.save(tpl)

    await repo.delete(tpl.id)
    assert await repo.get_by_id(tpl.id) is None
