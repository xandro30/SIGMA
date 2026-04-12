"""Tests unit de los use cases del agregado Week."""
from datetime import date, timedelta

import pytest

from sigma_core.planning.application.use_cases.day_template.create_day_template import (
    CreateDayTemplate,
    CreateDayTemplateCommand,
    DayTemplateBlockSpec,
)
from sigma_core.planning.application.use_cases.week.apply_template_to_week import (
    ApplyTemplateToWeek,
    ApplyTemplateToWeekCommand,
)
from sigma_core.planning.application.use_cases.week.create_week import (
    CreateWeek,
    CreateWeekCommand,
)
from sigma_core.planning.application.use_cases.week.delete_week import (
    DeleteWeek,
    DeleteWeekCommand,
)
from sigma_core.planning.application.use_cases.week.get_week import (
    GetWeek,
    GetWeekQuery,
)
from sigma_core.planning.application.use_cases.week.set_week_notes import (
    SetWeekNotes,
    SetWeekNotesCommand,
)
from sigma_core.planning.application.use_cases.week_template.create_week_template import (
    CreateWeekTemplate,
    CreateWeekTemplateCommand,
)
from sigma_core.planning.application.use_cases.week_template.set_slot import (
    SetWeekTemplateSlot,
    SetWeekTemplateSlotCommand,
)
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.errors import (
    CrossSpaceReferenceError,
    InvalidWeekStartError,
    WeekNotFoundError,
    WeekTemplateNotFoundError,
)
from sigma_core.planning.domain.value_objects import (
    DateRange,
    DayId,
    DayTemplateId,
    TimeOfDay,
    WeekId,
    WeekTemplateId,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId


MONDAY = date(2026, 4, 13)
WEDNESDAY = date(2026, 4, 15)


# ── Fakes inline (paralelos a los de los otros test files del mismo BC) ──


class FakeWeekRepository:
    def __init__(self) -> None:
        self._store: dict[str, Week] = {}

    async def save(self, week: Week) -> None:
        self._store[week.id.value] = week

    async def get_by_id(self, week_id: WeekId) -> Week | None:
        return self._store.get(week_id.value)

    async def delete(self, week_id: WeekId) -> None:
        self._store.pop(week_id.value, None)


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


# ── Helpers ─────────────────────────────────────────────────────


def _block_spec(
    *, hour: int = 9, minute: int = 0, duration: int = 60
) -> DayTemplateBlockSpec:
    return DayTemplateBlockSpec(
        start_at=TimeOfDay(hour=hour, minute=minute),
        duration=Minutes(duration),
        area_id=None,
        notes="",
    )


async def _seeded_week_template(
    *,
    week_template_repo: FakeWeekTemplateRepository,
    day_template_repo: FakeDayTemplateRepository,
    space_id: SpaceId,
) -> WeekTemplateId:
    wt_id = await CreateWeekTemplate(week_template_repo=week_template_repo).execute(
        CreateWeekTemplateCommand(space_id=space_id, name="WT")
    )
    slot_setter = SetWeekTemplateSlot(
        week_template_repo=week_template_repo,
        day_template_repo=day_template_repo,
    )
    dt_mon = await CreateDayTemplate(
        day_template_repo=day_template_repo
    ).execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="DT-mon",
            blocks=[_block_spec(hour=9, duration=60)],
        )
    )
    await slot_setter.execute(
        SetWeekTemplateSlotCommand(
            week_template_id=wt_id,
            day=DayOfWeek.MONDAY,
            day_template_id=dt_mon,
        )
    )
    dt_wed = await CreateDayTemplate(
        day_template_repo=day_template_repo
    ).execute(
        CreateDayTemplateCommand(
            space_id=space_id,
            name="DT-wed",
            blocks=[_block_spec(hour=14, duration=90)],
        )
    )
    await slot_setter.execute(
        SetWeekTemplateSlotCommand(
            week_template_id=wt_id,
            day=DayOfWeek.WEDNESDAY,
            day_template_id=dt_wed,
        )
    )
    return wt_id


# ── CreateWeek ─────────────────────────────────────────────────


class TestCreateWeek:
    @pytest.mark.asyncio
    async def test_crea_week_con_id_determinista(self):
        repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        uc = CreateWeek(week_repo=repo)

        week_id = await uc.execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )

        assert week_id == WeekId.for_space_and_week_start(space_id, MONDAY)
        stored = await repo.get_by_id(week_id)
        assert stored is not None
        assert stored.week_start == MONDAY
        assert stored.notes == ""
        assert stored.applied_template_id is None

    @pytest.mark.asyncio
    async def test_idempotente_si_ya_existe(self):
        repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        uc = CreateWeek(week_repo=repo)

        first = await uc.execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        second = await uc.execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )

        assert first == second

    @pytest.mark.asyncio
    async def test_rechaza_week_start_que_no_sea_lunes(self):
        repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        uc = CreateWeek(week_repo=repo)

        with pytest.raises(InvalidWeekStartError):
            await uc.execute(
                CreateWeekCommand(space_id=space_id, week_start=WEDNESDAY)
            )


# ── GetWeek ────────────────────────────────────────────────────


class TestGetWeek:
    @pytest.mark.asyncio
    async def test_devuelve_week_existente(self):
        repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        uc = GetWeek(week_repo=repo)

        result = await uc.execute(GetWeekQuery(week_id=week_id))

        assert result.id == week_id
        assert result.week_start == MONDAY

    @pytest.mark.asyncio
    async def test_lanza_week_not_found_si_no_existe(self):
        repo = FakeWeekRepository()
        uc = GetWeek(week_repo=repo)

        with pytest.raises(WeekNotFoundError):
            await uc.execute(GetWeekQuery(week_id=WeekId.generate()))


# ── SetWeekNotes ───────────────────────────────────────────────


class TestSetWeekNotes:
    @pytest.mark.asyncio
    async def test_actualiza_notas(self):
        repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        uc = SetWeekNotes(week_repo=repo)

        await uc.execute(
            SetWeekNotesCommand(week_id=week_id, notes="Testing week")
        )

        reloaded = await repo.get_by_id(week_id)
        assert reloaded is not None
        assert reloaded.notes == "Testing week"

    @pytest.mark.asyncio
    async def test_lanza_week_not_found(self):
        repo = FakeWeekRepository()
        uc = SetWeekNotes(week_repo=repo)

        with pytest.raises(WeekNotFoundError):
            await uc.execute(
                SetWeekNotesCommand(week_id=WeekId.generate(), notes="x")
            )


# ── ApplyTemplateToWeek ────────────────────────────────────────


class TestApplyTemplateToWeek:
    @pytest.mark.asyncio
    async def test_materializa_slots_y_registra_template_en_week(self):
        week_repo = FakeWeekRepository()
        week_template_repo = FakeWeekTemplateRepository()
        day_template_repo = FakeDayTemplateRepository()
        day_repo = FakeDayRepository()

        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=week_repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        wt_id = await _seeded_week_template(
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            space_id=space_id,
        )

        uc = ApplyTemplateToWeek(
            week_repo=week_repo,
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            day_repo=day_repo,
        )

        touched = await uc.execute(
            ApplyTemplateToWeekCommand(
                week_id=week_id, template_id=wt_id
            )
        )

        assert len(touched) == 2
        monday_day = await day_repo.get_by_id(
            DayId.for_space_and_date(space_id, MONDAY)
        )
        assert monday_day is not None
        assert len(monday_day.blocks) == 1
        wednesday_day = await day_repo.get_by_id(
            DayId.for_space_and_date(space_id, WEDNESDAY)
        )
        assert wednesday_day is not None
        assert len(wednesday_day.blocks) == 1
        reloaded_week = await week_repo.get_by_id(week_id)
        assert reloaded_week is not None
        assert reloaded_week.applied_template_id == wt_id

    @pytest.mark.asyncio
    async def test_rechaza_week_de_space_distinto_que_template(self):
        week_repo = FakeWeekRepository()
        week_template_repo = FakeWeekTemplateRepository()
        day_template_repo = FakeDayTemplateRepository()
        day_repo = FakeDayRepository()

        space_a = SpaceId.generate()
        space_b = SpaceId.generate()
        week_id = await CreateWeek(week_repo=week_repo).execute(
            CreateWeekCommand(space_id=space_a, week_start=MONDAY)
        )
        wt_id = await _seeded_week_template(
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            space_id=space_b,
        )

        uc = ApplyTemplateToWeek(
            week_repo=week_repo,
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            day_repo=day_repo,
        )

        with pytest.raises(CrossSpaceReferenceError):
            await uc.execute(
                ApplyTemplateToWeekCommand(
                    week_id=week_id, template_id=wt_id
                )
            )

    @pytest.mark.asyncio
    async def test_lanza_week_not_found(self):
        uc = ApplyTemplateToWeek(
            week_repo=FakeWeekRepository(),
            week_template_repo=FakeWeekTemplateRepository(),
            day_template_repo=FakeDayTemplateRepository(),
            day_repo=FakeDayRepository(),
        )
        with pytest.raises(WeekNotFoundError):
            await uc.execute(
                ApplyTemplateToWeekCommand(
                    week_id=WeekId.generate(),
                    template_id=WeekTemplateId.generate(),
                )
            )

    @pytest.mark.asyncio
    async def test_lanza_week_template_not_found(self):
        week_repo = FakeWeekRepository()
        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=week_repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        uc = ApplyTemplateToWeek(
            week_repo=week_repo,
            week_template_repo=FakeWeekTemplateRepository(),
            day_template_repo=FakeDayTemplateRepository(),
            day_repo=FakeDayRepository(),
        )
        with pytest.raises(WeekTemplateNotFoundError):
            await uc.execute(
                ApplyTemplateToWeekCommand(
                    week_id=week_id, template_id=WeekTemplateId.generate()
                )
            )


# ── DeleteWeek ─────────────────────────────────────────────────


class TestDeleteWeek:
    @pytest.mark.asyncio
    async def test_borra_week_y_cascada_dias_materializados(self):
        week_repo = FakeWeekRepository()
        week_template_repo = FakeWeekTemplateRepository()
        day_template_repo = FakeDayTemplateRepository()
        day_repo = FakeDayRepository()

        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=week_repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )
        wt_id = await _seeded_week_template(
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            space_id=space_id,
        )
        await ApplyTemplateToWeek(
            week_repo=week_repo,
            week_template_repo=week_template_repo,
            day_template_repo=day_template_repo,
            day_repo=day_repo,
        ).execute(
            ApplyTemplateToWeekCommand(week_id=week_id, template_id=wt_id)
        )

        uc = DeleteWeek(week_repo=week_repo, day_repo=day_repo)
        await uc.execute(DeleteWeekCommand(week_id=week_id))

        assert await week_repo.get_by_id(week_id) is None
        for offset in range(7):
            d = MONDAY + timedelta(days=offset)
            assert (
                await day_repo.get_by_id(
                    DayId.for_space_and_date(space_id, d)
                )
                is None
            )

    @pytest.mark.asyncio
    async def test_borrar_week_sin_dias_materializados_es_noop_para_days(self):
        week_repo = FakeWeekRepository()
        day_repo = FakeDayRepository()
        space_id = SpaceId.generate()
        week_id = await CreateWeek(week_repo=week_repo).execute(
            CreateWeekCommand(space_id=space_id, week_start=MONDAY)
        )

        await DeleteWeek(week_repo=week_repo, day_repo=day_repo).execute(
            DeleteWeekCommand(week_id=week_id)
        )

        assert await week_repo.get_by_id(week_id) is None

    @pytest.mark.asyncio
    async def test_lanza_week_not_found(self):
        uc = DeleteWeek(
            week_repo=FakeWeekRepository(),
            day_repo=FakeDayRepository(),
        )
        with pytest.raises(WeekNotFoundError):
            await uc.execute(DeleteWeekCommand(week_id=WeekId.generate()))
