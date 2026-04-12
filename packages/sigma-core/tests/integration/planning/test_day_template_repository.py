import pytest

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.planning.infrastructure.firestore.day_template_repository import (
    FirestoreDayTemplateRepository,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId


def _template(space_id: SpaceId, *, name: str = "Día estándar") -> DayTemplate:
    return DayTemplate(
        id=DayTemplateId.generate(),
        space_id=space_id,
        name=name,
        blocks=[
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=9, minute=0),
                duration=Minutes(60),
                area_id=AreaId.generate(),
                notes="deep work",
            ),
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=14, minute=30),
                duration=Minutes(30),
                area_id=None,
                notes="",
            ),
        ],
    )


@pytest.mark.asyncio
async def test_save_and_get_day_template(firestore_client):
    repo = FirestoreDayTemplateRepository(firestore_client)
    tpl = _template(SpaceId.generate())

    await repo.save(tpl)
    result = await repo.get_by_id(tpl.id)

    assert result is not None
    assert result.id == tpl.id
    assert result.name == tpl.name
    assert len(result.blocks) == 2
    assert result.blocks[0].start_at == TimeOfDay(hour=9, minute=0)
    assert result.blocks[1].start_at == TimeOfDay(hour=14, minute=30)


@pytest.mark.asyncio
async def test_get_day_template_not_found(firestore_client):
    repo = FirestoreDayTemplateRepository(firestore_client)
    assert await repo.get_by_id(DayTemplateId.generate()) is None


@pytest.mark.asyncio
async def test_list_by_space(firestore_client):
    repo = FirestoreDayTemplateRepository(firestore_client)
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()

    await repo.save(_template(space_a, name="A1"))
    await repo.save(_template(space_a, name="A2"))
    await repo.save(_template(space_b, name="B1"))

    result = await repo.list_by_space(space_a)
    assert {t.name for t in result} == {"A1", "A2"}


@pytest.mark.asyncio
async def test_delete_day_template(firestore_client):
    repo = FirestoreDayTemplateRepository(firestore_client)
    tpl = _template(SpaceId.generate())
    await repo.save(tpl)

    await repo.delete(tpl.id)
    assert await repo.get_by_id(tpl.id) is None
