from datetime import date, datetime, timezone

import pytest

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DateRange,
    DayId,
)
from sigma_core.planning.infrastructure.firestore.day_repository import (
    FirestoreDayRepository,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


def _day(
    space_id: SpaceId,
    *,
    on: date = date(2026, 4, 10),
    blocks: list[TimeBlock] | None = None,
) -> Day:
    return Day(
        id=DayId.generate(),
        space_id=space_id,
        date=on,
        blocks=blocks or [],
    )


@pytest.mark.asyncio
async def test_save_and_get_day(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    day = _day(SpaceId.generate())

    await repo.save(day)
    result = await repo.get_by_id(day.id)

    assert result is not None
    assert result.id == day.id
    assert result.date == day.date


@pytest.mark.asyncio
async def test_get_day_not_found(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    assert await repo.get_by_id(DayId.generate()) is None


@pytest.mark.asyncio
async def test_get_by_space_and_date(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    space_id = SpaceId.generate()
    target = date(2026, 4, 10)
    other = date(2026, 4, 11)

    day_target = _day(space_id, on=target)
    day_other = _day(space_id, on=other)
    await repo.save(day_target)
    await repo.save(day_other)

    result = await repo.get_by_space_and_date(space_id, target)

    assert result is not None
    assert result.id == day_target.id


@pytest.mark.asyncio
async def test_get_by_space_and_date_miss(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    assert (
        await repo.get_by_space_and_date(SpaceId.generate(), date(2026, 4, 10))
        is None
    )


@pytest.mark.asyncio
async def test_list_by_space_and_range(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    space_id = SpaceId.generate()
    d1 = _day(space_id, on=date(2026, 4, 10))
    d2 = _day(space_id, on=date(2026, 4, 15))
    d_outside = _day(space_id, on=date(2026, 5, 1))
    for d in (d1, d2, d_outside):
        await repo.save(d)

    result = await repo.list_by_space_and_range(
        space_id,
        DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30)),
    )

    assert {d.id for d in result} == {d1.id, d2.id}


@pytest.mark.asyncio
async def test_delete_day(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    day = _day(SpaceId.generate())
    await repo.save(day)

    await repo.delete(day.id)
    assert await repo.get_by_id(day.id) is None


@pytest.mark.asyncio
async def test_round_trip_day_con_bloques(firestore_client):
    repo = FirestoreDayRepository(firestore_client)
    target = date(2026, 4, 10)
    area_id = AreaId.generate()
    block = TimeBlock(
        id=BlockId.generate(),
        start_at=Timestamp(datetime(2026, 4, 10, 9, 0, tzinfo=timezone.utc)),
        duration=Minutes(90),
        area_id=area_id,
        notes="foco",
    )
    day = _day(SpaceId.generate(), on=target, blocks=[block])

    await repo.save(day)
    result = await repo.get_by_id(day.id)

    assert result is not None
    assert len(result.blocks) == 1
    assert result.blocks[0].id == block.id
    assert result.blocks[0].duration == Minutes(90)
    assert result.blocks[0].area_id == area_id
    assert result.blocks[0].notes == "foco"
