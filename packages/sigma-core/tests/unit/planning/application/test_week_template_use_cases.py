from datetime import date

import pytest

from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    CreateDayTemplate,
    CreateDayTemplateCommand,
    DayTemplateBlockSpec,
)
from sigma_core.planning.application.use_cases.week_template.clear_slot import (
    ClearWeekTemplateSlot,
    ClearWeekTemplateSlotCommand,
)
from sigma_core.planning.application.use_cases.week_template.create_week_template import (
    CreateWeekTemplate,
    CreateWeekTemplateCommand,
)
from sigma_core.planning.application.use_cases.week_template.delete_week_template import (
    DeleteWeekTemplate,
    DeleteWeekTemplateCommand,
)
from sigma_core.planning.application.use_cases.week_template.set_slot import (
    SetWeekTemplateSlot,
    SetWeekTemplateSlotCommand,
)
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.errors import (
    CrossSpaceReferenceError,
    DayTemplateNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.planning.domain.value_objects import (
    DateRange,
    DayId,
    DayTemplateId,
    TimeOfDay,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId


# ── Fakes ────────────────────────────────────────────────────────


class FakeWeekTemplateRepository:
    def __init__(self) -> None:
        self._store: dict[str, WeekTemplate] = {}

    async def save(self, template: WeekTemplate) -> None:
        self._store[template.id.value] = template

    async def get_by_id(
        self, template_id: WeekTemplateId
    ) -> WeekTemplate | None:
        return self._store.get(template_id.value)

    async def list_by_space(self, space_id: SpaceId) -> list[WeekTemplate]:
        return [t for t in self._store.values() if t.space_id == space_id]

    async def delete(self, template_id: WeekTemplateId) -> None:
        self._store.pop(template_id.value, None)


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
        return [t for t in self._store.values() if t.space_id == space_id]

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


def _block_spec(hour: int, duration: int = 60) -> DayTemplateBlockSpec:
    return DayTemplateBlockSpec(
        start_at=TimeOfDay(hour=hour, minute=0),
        duration=Minutes(duration),
        area_id=None,
    )


# ── CreateWeekTemplate ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_week_template_persiste_con_nombre():
    repo = FakeWeekTemplateRepository()
    uc = CreateWeekTemplate(week_template_repo=repo)

    template_id = await uc.execute(
        CreateWeekTemplateCommand(
            space_id=SpaceId.generate(), name="Semana estandar"
        )
    )

    stored = await repo.get_by_id(template_id)
    assert stored is not None
    assert stored.name == "Semana estandar"
    assert all(v is None for v in stored.slots.values())


# ── SetWeekTemplateSlot / ClearWeekTemplateSlot ─────────────


@pytest.mark.asyncio
async def test_set_slot_asigna_day_template():
    week_repo = FakeWeekTemplateRepository()
    day_template_repo = FakeDayTemplateRepository()
    space_id = SpaceId.generate()

    create_wt = CreateWeekTemplate(week_template_repo=week_repo)
    wt_id = await create_wt.execute(
        CreateWeekTemplateCommand(space_id=space_id, name="W")
    )

    create_dt = CreateDayTemplate(day_template_repo=day_template_repo)
    dt_id = await create_dt.execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="D",
            blocks=[_block_spec(hour=9)],
        )
    )

    uc = SetWeekTemplateSlot(
        week_template_repo=week_repo,
        day_template_repo=day_template_repo,
    )
    await uc.execute(
        SetWeekTemplateSlotCommand(
            week_template_id=wt_id,
            day=DayOfWeek.MONDAY,
            day_template_id=dt_id,
        )
    )

    reloaded = await week_repo.get_by_id(wt_id)
    assert reloaded is not None
    assert reloaded.slots[DayOfWeek.MONDAY] == dt_id


@pytest.mark.asyncio
async def test_set_slot_falla_si_day_template_no_existe():
    week_repo = FakeWeekTemplateRepository()
    day_template_repo = FakeDayTemplateRepository()
    space_id = SpaceId.generate()

    create_wt = CreateWeekTemplate(week_template_repo=week_repo)
    wt_id = await create_wt.execute(
        CreateWeekTemplateCommand(space_id=space_id, name="W")
    )

    uc = SetWeekTemplateSlot(
        week_template_repo=week_repo,
        day_template_repo=day_template_repo,
    )
    with pytest.raises(DayTemplateNotFoundError):
        await uc.execute(
            SetWeekTemplateSlotCommand(
                week_template_id=wt_id,
                day=DayOfWeek.MONDAY,
                day_template_id=DayTemplateId.generate(),
            )
        )


@pytest.mark.asyncio
async def test_set_slot_rechaza_day_template_de_otro_space():
    """El DayTemplate referenciado debe pertenecer al mismo Space que
    el WeekTemplate — cross-space references rompen el aislamiento por Space."""
    week_repo = FakeWeekTemplateRepository()
    day_template_repo = FakeDayTemplateRepository()
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()

    wt_id = await CreateWeekTemplate(week_template_repo=week_repo).execute(
        CreateWeekTemplateCommand(space_id=space_a, name="W-A")
    )
    dt_id = await CreateDayTemplate(day_template_repo=day_template_repo).execute(
        CreateDayTemplateCommand(
            space_id=space_b,
            name="D-B",
            blocks=[_block_spec(hour=9)],
        )
    )

    uc = SetWeekTemplateSlot(
        week_template_repo=week_repo,
        day_template_repo=day_template_repo,
    )
    with pytest.raises(CrossSpaceReferenceError):
        await uc.execute(
            SetWeekTemplateSlotCommand(
                week_template_id=wt_id,
                day=DayOfWeek.MONDAY,
                day_template_id=dt_id,
            )
        )


@pytest.mark.asyncio
async def test_clear_slot_pone_a_none():
    week_repo = FakeWeekTemplateRepository()
    day_template_repo = FakeDayTemplateRepository()
    space_id = SpaceId.generate()

    create_wt = CreateWeekTemplate(week_template_repo=week_repo)
    wt_id = await create_wt.execute(
        CreateWeekTemplateCommand(space_id=space_id, name="W")
    )
    dt_id = await CreateDayTemplate(day_template_repo=day_template_repo).execute(
        CreateDayTemplateCommand(
            space_id=space_id, name="D", blocks=[_block_spec(hour=9)]
        )
    )
    await SetWeekTemplateSlot(
        week_template_repo=week_repo, day_template_repo=day_template_repo
    ).execute(
        SetWeekTemplateSlotCommand(
            week_template_id=wt_id,
            day=DayOfWeek.MONDAY,
            day_template_id=dt_id,
        )
    )

    clear_uc = ClearWeekTemplateSlot(week_template_repo=week_repo)
    await clear_uc.execute(
        ClearWeekTemplateSlotCommand(
            week_template_id=wt_id, day=DayOfWeek.MONDAY
        )
    )

    reloaded = await week_repo.get_by_id(wt_id)
    assert reloaded is not None
    assert reloaded.slots[DayOfWeek.MONDAY] is None


# ── DeleteWeekTemplate ─────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_week_template_falla_si_no_existe():
    repo = FakeWeekTemplateRepository()
    uc = DeleteWeekTemplate(week_template_repo=repo)

    with pytest.raises(WeekTemplateNotFoundError):
        await uc.execute(
            DeleteWeekTemplateCommand(template_id=WeekTemplateId.generate())
        )


