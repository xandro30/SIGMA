from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.application.use_cases.day.create_day import (
    CreateDay,
    CreateDayCommand,
)
from sigma_core.planning.application.use_cases.day_template.apply_template_to_day import (
    ApplyDayTemplateToDay,
    ApplyDayTemplateToDayCommand,
    DayTemplateBlockSpec,
)
from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    CreateDayTemplate,
    CreateDayTemplateCommand,
)
from sigma_core.planning.application.use_cases.day_template.delete_day_template import (
    DeleteDayTemplate,
    DeleteDayTemplateCommand,
)
from sigma_core.planning.application.use_cases.day_template.update_day_template import (
    UpdateDayTemplate,
    UpdateDayTemplateCommand,
)
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import (
    DayNotEmptyError,
    DayTemplateNotFoundError,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DateRange,
    DayId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId, Timestamp


MADRID = ZoneInfo("Europe/Madrid")
TARGET_DATE = date(2026, 4, 13)


def ts(hour: int, minute: int = 0) -> Timestamp:
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


# ── Fakes ────────────────────────────────────────────────────────


class FakeDayTemplateRepository:
    def __init__(self) -> None:
        self._store: dict[str, DayTemplate] = {}

    async def save(self, template: DayTemplate) -> None:
        self._store[template.id.value] = template

    async def get_by_id(
        self, template_id: DayTemplateId
    ) -> DayTemplate | None:
        return self._store.get(template_id.value)

    async def list_by_space(self, space_id: SpaceId) -> list[DayTemplate]:
        return [
            t for t in self._store.values() if t.space_id == space_id
        ]

    async def delete(self, template_id: DayTemplateId) -> None:
        self._store.pop(template_id.value, None)


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
        for d in self._store.values():
            if d.space_id == space_id and d.date == target_date:
                return d
        return None

    async def list_by_space_and_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[Day]:
        return [
            d
            for d in self._store.values()
            if d.space_id == space_id and date_range.contains(d.date)
        ]

    async def delete(self, day_id: DayId) -> None:
        self._store.pop(day_id.value, None)


def _block_spec(
    hour: int, duration_minutes: int = 60, notes: str = ""
) -> DayTemplateBlockSpec:
    return DayTemplateBlockSpec(
        start_at=TimeOfDay(hour=hour, minute=0),
        duration=Minutes(duration_minutes),
        area_id=None,
        notes=notes,
    )


# ── CreateDayTemplate ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_day_template_persiste_con_bloques():
    repo = FakeDayTemplateRepository()
    uc = CreateDayTemplate(day_template_repo=repo)

    template_id = await uc.execute(
        CreateDayTemplateCommand(
            space_id=SpaceId.generate(),
            name="Lunes tipo",
            blocks=[
                _block_spec(hour=9, duration_minutes=60),
                _block_spec(hour=11, duration_minutes=30),
            ],
        )
    )

    stored = await repo.get_by_id(template_id)
    assert stored is not None
    assert stored.name == "Lunes tipo"
    assert len(stored.blocks) == 2
    assert stored.blocks[0].start_at == TimeOfDay(hour=9, minute=0)


# ── UpdateDayTemplate ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_day_template_reemplaza_bloques_y_nombre():
    repo = FakeDayTemplateRepository()
    template = DayTemplate(
        id=DayTemplateId.generate(),
        space_id=SpaceId.generate(),
        name="Original",
    )
    template.add_block(
        DayTemplateBlock(
            id=BlockId.generate(),
            start_at=TimeOfDay(hour=9, minute=0),
            duration=Minutes(60),
            area_id=None,
        )
    )
    repo._store[template.id.value] = template
    uc = UpdateDayTemplate(day_template_repo=repo)

    await uc.execute(
        UpdateDayTemplateCommand(
            template_id=template.id,
            name="Renombrado",
            blocks=[_block_spec(hour=14, duration_minutes=120)],
        )
    )

    reloaded = await repo.get_by_id(template.id)
    assert reloaded is not None
    assert reloaded.name == "Renombrado"
    assert len(reloaded.blocks) == 1
    assert reloaded.blocks[0].start_at == TimeOfDay(hour=14, minute=0)


@pytest.mark.asyncio
async def test_update_day_template_falla_si_no_existe():
    repo = FakeDayTemplateRepository()
    uc = UpdateDayTemplate(day_template_repo=repo)

    with pytest.raises(DayTemplateNotFoundError):
        await uc.execute(
            UpdateDayTemplateCommand(
                template_id=DayTemplateId.generate(),
                name="X",
                blocks=[],
            )
        )


# ── DeleteDayTemplate ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_day_template_quita_del_repo():
    repo = FakeDayTemplateRepository()
    template = DayTemplate(
        id=DayTemplateId.generate(),
        space_id=SpaceId.generate(),
        name="X",
    )
    repo._store[template.id.value] = template
    uc = DeleteDayTemplate(day_template_repo=repo)

    await uc.execute(DeleteDayTemplateCommand(template_id=template.id))

    assert await repo.get_by_id(template.id) is None


@pytest.mark.asyncio
async def test_delete_day_template_falla_si_no_existe():
    repo = FakeDayTemplateRepository()
    uc = DeleteDayTemplate(day_template_repo=repo)

    with pytest.raises(DayTemplateNotFoundError):
        await uc.execute(
            DeleteDayTemplateCommand(template_id=DayTemplateId.generate())
        )


# ── ApplyDayTemplateToDay ──────────────────────────────────────


@pytest.mark.asyncio
async def test_apply_template_to_day_forka_bloques_en_dia_vacio():
    template_repo = FakeDayTemplateRepository()
    day_repo = FakeDayRepository()
    space_id = SpaceId.generate()

    create_template = CreateDayTemplate(day_template_repo=template_repo)
    template_id = await create_template.execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="Day type",
            blocks=[
                _block_spec(hour=9, duration_minutes=60),
                _block_spec(hour=11, duration_minutes=60),
            ],
        )
    )

    apply_uc = ApplyDayTemplateToDay(
        day_template_repo=template_repo, day_repo=day_repo
    )

    day_id = await apply_uc.execute(
        ApplyDayTemplateToDayCommand(
            template_id=template_id,
            space_id=space_id,
            target_date=TARGET_DATE,
            replace_existing=False,
        )
    )

    stored = await day_repo.get_by_id(day_id)
    assert stored is not None
    assert len(stored.blocks) == 2
    # Fechas absolutas derivadas del target_date
    assert stored.blocks[0].start_at.value.date() == TARGET_DATE
    assert stored.blocks[0].start_at.value.hour == 9


@pytest.mark.asyncio
async def test_apply_template_rechaza_day_no_vacio_sin_replace():
    template_repo = FakeDayTemplateRepository()
    day_repo = FakeDayRepository()
    space_id = SpaceId.generate()

    create_template = CreateDayTemplate(day_template_repo=template_repo)
    template_id = await create_template.execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="Day type",
            blocks=[_block_spec(hour=9)],
        )
    )

    create_day = CreateDay(day_repo=day_repo)
    day_id = await create_day.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )
    day = await day_repo.get_by_id(day_id)
    assert day is not None
    day.add_block(
        TimeBlock(
            id=BlockId.generate(),
            start_at=ts(15, 0),
            duration=Minutes(30),
            area_id=None,
        )
    )
    await day_repo.save(day)

    apply_uc = ApplyDayTemplateToDay(
        day_template_repo=template_repo, day_repo=day_repo
    )

    with pytest.raises(DayNotEmptyError):
        await apply_uc.execute(
            ApplyDayTemplateToDayCommand(
                template_id=template_id,
                space_id=space_id,
                target_date=TARGET_DATE,
                replace_existing=False,
            )
        )


@pytest.mark.asyncio
async def test_apply_template_reemplaza_bloques_con_replace_true():
    template_repo = FakeDayTemplateRepository()
    day_repo = FakeDayRepository()
    space_id = SpaceId.generate()

    create_template = CreateDayTemplate(day_template_repo=template_repo)
    template_id = await create_template.execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="Day type",
            blocks=[_block_spec(hour=9, duration_minutes=60)],
        )
    )
    create_day = CreateDay(day_repo=day_repo)
    day_id = await create_day.execute(
        CreateDayCommand(space_id=space_id, target_date=TARGET_DATE)
    )
    day = await day_repo.get_by_id(day_id)
    assert day is not None
    day.add_block(
        TimeBlock(
            id=BlockId.generate(),
            start_at=ts(15, 0),
            duration=Minutes(30),
            area_id=None,
        )
    )
    await day_repo.save(day)

    apply_uc = ApplyDayTemplateToDay(
        day_template_repo=template_repo, day_repo=day_repo
    )

    await apply_uc.execute(
        ApplyDayTemplateToDayCommand(
            template_id=template_id,
            space_id=space_id,
            target_date=TARGET_DATE,
            replace_existing=True,
        )
    )

    stored = await day_repo.get_by_id(day_id)
    assert stored is not None
    assert len(stored.blocks) == 1
    assert stored.blocks[0].start_at.value.hour == 9


@pytest.mark.asyncio
async def test_apply_template_falla_si_template_no_existe():
    template_repo = FakeDayTemplateRepository()
    day_repo = FakeDayRepository()
    uc = ApplyDayTemplateToDay(
        day_template_repo=template_repo, day_repo=day_repo
    )

    with pytest.raises(DayTemplateNotFoundError):
        await uc.execute(
            ApplyDayTemplateToDayCommand(
                template_id=DayTemplateId.generate(),
                space_id=SpaceId.generate(),
                target_date=TARGET_DATE,
                replace_existing=False,
            )
        )
