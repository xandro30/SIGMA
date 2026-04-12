from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.application.use_cases.day.add_block import (
    AddBlockToDay,
    AddBlockToDayCommand,
)
from sigma_core.planning.application.use_cases.day.clear_blocks import (
    ClearDayBlocks,
    ClearDayBlocksCommand,
)
from sigma_core.planning.application.use_cases.day.create_day import (
    CreateDay,
    CreateDayCommand,
)
from sigma_core.planning.application.use_cases.day.remove_block import (
    RemoveBlockFromDay,
    RemoveBlockFromDayCommand,
)
from sigma_core.planning.application.use_cases.day.update_block import (
    UpdateBlockInDay,
    UpdateBlockInDayCommand,
)
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    DayNotFoundError,
)
from sigma_core.planning.domain.value_objects import BlockId, DateRange, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MADRID = ZoneInfo("Europe/Madrid")
TARGET_DATE = date(2026, 4, 13)


def at(hour: int, minute: int = 0) -> Timestamp:
    return Timestamp(
        datetime(
            TARGET_DATE.year,
            TARGET_DATE.month,
            TARGET_DATE.day,
            hour,
            minute,
            tzinfo=MADRID,
        )
    )


class FakeDayRepository:
    def __init__(self) -> None:
        self._store: dict[str, Day] = {}

    async def save(self, day: Day) -> None:
        self._store[day.id.value] = day

    async def get_by_id(self, day_id: DayId) -> Day | None:
        return self._store.get(day_id.value)

    async def get_by_space_and_date(
        self, space_id: SpaceId, target_date: date
    ) -> Day | None:
        for day in self._store.values():
            if day.space_id == space_id and day.date == target_date:
                return day
        return None

    async def list_by_space_and_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[Day]:
        return [
            day
            for day in self._store.values()
            if day.space_id == space_id and date_range.contains(day.date)
        ]

    async def delete(self, day_id: DayId) -> None:
        self._store.pop(day_id.value, None)


def _seed_day(repo: FakeDayRepository, space_id: SpaceId) -> Day:
    day = Day(
        id=DayId.for_space_and_date(space_id, TARGET_DATE),
        space_id=space_id,
        date=TARGET_DATE,
    )
    repo._store[day.id.value] = day
    return day


# ── CreateDay ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_day_devuelve_id_existente_si_ya_hay_day():
    repo = FakeDayRepository()
    space_id = SpaceId.generate()
    existing = _seed_day(repo, space_id)
    uc = CreateDay(day_repo=repo)

    day_id = await uc.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )

    assert day_id == existing.id


@pytest.mark.asyncio
async def test_create_day_crea_nuevo_vacio_si_no_existe():
    repo = FakeDayRepository()
    space_id = SpaceId.generate()
    uc = CreateDay(day_repo=repo)

    day_id = await uc.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )

    stored = await repo.get_by_id(day_id)
    assert stored is not None
    assert stored.blocks == []
    assert stored.date == TARGET_DATE


@pytest.mark.asyncio
async def test_create_day_es_determinista_para_mismo_space_y_fecha():
    """Dos CreateDay con mismos (space, date) producen el mismo DayId.

    Elimina la race condition: en concurrencia, ambos requests escriben
    el mismo document_id y Firestore deduplica naturalmente con `.set()`.
    """
    repo = FakeDayRepository()
    space_id = SpaceId.generate()
    uc = CreateDay(day_repo=repo)

    first = await uc.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )
    second = await uc.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )

    assert first == second
    assert first == DayId.for_space_and_date(space_id, TARGET_DATE)


# ── AddBlockToDay ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_block_anade_al_day():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    uc = AddBlockToDay(day_repo=repo)

    await uc.execute(
        AddBlockToDayCommand(
            day_id=day.id,
            start_at=at(9),
            duration=Minutes(60),
            area_id=None,
            notes="",
        )
    )

    reloaded = await repo.get_by_id(day.id)
    assert reloaded is not None
    assert len(reloaded.blocks) == 1


@pytest.mark.asyncio
async def test_add_block_propaga_overlap_error():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    uc = AddBlockToDay(day_repo=repo)

    await uc.execute(
        AddBlockToDayCommand(
            day_id=day.id,
            start_at=at(9),
            duration=Minutes(60),
            area_id=None,
            notes="",
        )
    )

    with pytest.raises(BlockOverlapError):
        await uc.execute(
            AddBlockToDayCommand(
                day_id=day.id,
                start_at=at(9, 30),
                duration=Minutes(30),
                area_id=None,
                notes="",
            )
        )


@pytest.mark.asyncio
async def test_add_block_falla_si_day_no_existe():
    repo = FakeDayRepository()
    uc = AddBlockToDay(day_repo=repo)

    with pytest.raises(DayNotFoundError):
        await uc.execute(
            AddBlockToDayCommand(
                day_id=DayId.generate(),
                start_at=at(9),
                duration=Minutes(60),
                area_id=None,
                notes="",
            )
        )


# ── UpdateBlockInDay ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_block_cambia_duration():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    block = TimeBlock(
        id=BlockId.generate(),
        start_at=at(9),
        duration=Minutes(60),
        area_id=None,
    )
    day.add_block(block)
    uc = UpdateBlockInDay(day_repo=repo)

    await uc.execute(
        UpdateBlockInDayCommand(
            day_id=day.id,
            block_id=block.id,
            start_at=None,
            duration=Minutes(30),
            area_id_set=False,
            area_id=None,
            notes=None,
        )
    )

    reloaded = await repo.get_by_id(day.id)
    assert reloaded is not None
    assert reloaded.blocks[0].duration == Minutes(30)


@pytest.mark.asyncio
async def test_update_block_puede_desasignar_area():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    area_id = AreaId.generate()
    block = TimeBlock(
        id=BlockId.generate(),
        start_at=at(9),
        duration=Minutes(60),
        area_id=area_id,
    )
    day.add_block(block)
    uc = UpdateBlockInDay(day_repo=repo)

    await uc.execute(
        UpdateBlockInDayCommand(
            day_id=day.id,
            block_id=block.id,
            start_at=None,
            duration=None,
            area_id_set=True,
            area_id=None,
            notes=None,
        )
    )

    reloaded = await repo.get_by_id(day.id)
    assert reloaded is not None
    assert reloaded.blocks[0].area_id is None


@pytest.mark.asyncio
async def test_update_block_falla_si_block_no_existe():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    uc = UpdateBlockInDay(day_repo=repo)

    with pytest.raises(BlockNotFoundError):
        await uc.execute(
            UpdateBlockInDayCommand(
                day_id=day.id,
                block_id=BlockId.generate(),
                start_at=None,
                duration=None,
                area_id_set=False,
                area_id=None,
                notes="x",
            )
        )


# ── RemoveBlockFromDay ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_remove_block_elimina_del_day():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    block = TimeBlock(
        id=BlockId.generate(),
        start_at=at(9),
        duration=Minutes(60),
        area_id=None,
    )
    day.add_block(block)
    uc = RemoveBlockFromDay(day_repo=repo)

    await uc.execute(
        RemoveBlockFromDayCommand(day_id=day.id, block_id=block.id)
    )

    reloaded = await repo.get_by_id(day.id)
    assert reloaded is not None
    assert reloaded.blocks == []


@pytest.mark.asyncio
async def test_remove_block_falla_si_day_no_existe():
    repo = FakeDayRepository()
    uc = RemoveBlockFromDay(day_repo=repo)

    with pytest.raises(DayNotFoundError):
        await uc.execute(
            RemoveBlockFromDayCommand(
                day_id=DayId.generate(), block_id=BlockId.generate()
            )
        )


# ── ClearDayBlocks ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_clear_day_blocks_vacia_lista():
    repo = FakeDayRepository()
    day = _seed_day(repo, SpaceId.generate())
    day.add_block(
        TimeBlock(
            id=BlockId.generate(),
            start_at=at(9),
            duration=Minutes(60),
            area_id=None,
        )
    )
    day.add_block(
        TimeBlock(
            id=BlockId.generate(),
            start_at=at(11),
            duration=Minutes(60),
            area_id=None,
        )
    )
    uc = ClearDayBlocks(day_repo=repo)

    await uc.execute(ClearDayBlocksCommand(day_id=day.id))

    reloaded = await repo.get_by_id(day.id)
    assert reloaded is not None
    assert reloaded.blocks == []


@pytest.mark.asyncio
async def test_clear_day_blocks_falla_si_day_no_existe():
    repo = FakeDayRepository()
    uc = ClearDayBlocks(day_repo=repo)

    with pytest.raises(DayNotFoundError):
        await uc.execute(ClearDayBlocksCommand(day_id=DayId.generate()))
