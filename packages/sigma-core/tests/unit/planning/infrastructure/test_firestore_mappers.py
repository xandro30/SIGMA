"""Round-trip tests for Firestore mappers del BC planning.

Son tests unitarios (no requieren emulator): serializamos a dict, deserializamos
y comprobamos equivalencia. El objetivo es blindar que un escribe+lee mantiene
la identidad del agregado.
"""
from datetime import date, datetime, timezone

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.enums import CycleState, DayOfWeek
from sigma_core.planning.domain.errors import (
    BlockOverlapError,
    InvalidTimeBlockError,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    CycleId,
    DateRange,
    DayId,
    DayTemplateId,
    TimeOfDay,
    WeekId,
    WeekTemplateId,
)
from sigma_core.planning.infrastructure.firestore.mappers import (
    cycle_from_dict,
    cycle_to_dict,
    day_from_dict,
    day_template_from_dict,
    day_template_to_dict,
    day_to_dict,
    week_from_dict,
    week_template_from_dict,
    week_template_to_dict,
    week_to_dict,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


def _ts(year: int, month: int, day: int, hour: int = 12) -> Timestamp:
    return Timestamp(datetime(year, month, day, hour, 0, tzinfo=timezone.utc))


# ── Cycle ─────────────────────────────────────────────────────────


class TestCycleMapper:
    def test_round_trip_cycle_completo(self):
        area_a = AreaId.generate()
        area_b = AreaId.generate()
        original = Cycle(
            id=CycleId.generate(),
            space_id=SpaceId.generate(),
            name="Abril",
            date_range=DateRange(
                start=date(2026, 4, 1), end=date(2026, 4, 30)
            ),
            state=CycleState.ACTIVE,
            area_budgets={area_a: Minutes(600), area_b: Minutes(300)},
            buffer_percentage=20,
        )

        data = cycle_to_dict(original)
        rehydrated = cycle_from_dict(data)

        assert rehydrated.id == original.id
        assert rehydrated.space_id == original.space_id
        assert rehydrated.name == original.name
        assert rehydrated.date_range == original.date_range
        assert rehydrated.state == CycleState.ACTIVE
        assert rehydrated.area_budgets == original.area_budgets
        assert rehydrated.buffer_percentage == 20
        assert rehydrated.closed_at is None

    def test_round_trip_cycle_con_closed_at(self):
        original = Cycle(
            id=CycleId.generate(),
            space_id=SpaceId.generate(),
            name="Marzo",
            date_range=DateRange(
                start=date(2026, 3, 1), end=date(2026, 3, 31)
            ),
            state=CycleState.CLOSED,
            area_budgets={},
            buffer_percentage=10,
            closed_at=_ts(2026, 4, 1),
        )

        data = cycle_to_dict(original)
        rehydrated = cycle_from_dict(data)

        assert rehydrated.state == CycleState.CLOSED
        assert rehydrated.closed_at is not None


# ── Day + TimeBlock ──────────────────────────────────────────────


class TestDayMapper:
    def test_round_trip_day_con_bloques(self):
        day_date = date(2026, 4, 10)
        area_a = AreaId.generate()
        start = Timestamp(
            datetime(2026, 4, 10, 9, 0, tzinfo=timezone.utc)
        )
        block = TimeBlock(
            id=BlockId.generate(),
            start_at=start,
            duration=Minutes(60),
            area_id=area_a,
            notes="deep work",
        )
        original = Day(
            id=DayId.generate(),
            space_id=SpaceId.generate(),
            date=day_date,
            blocks=[block],
        )

        data = day_to_dict(original)
        rehydrated = day_from_dict(data)

        assert rehydrated.id == original.id
        assert rehydrated.date == day_date
        assert len(rehydrated.blocks) == 1
        assert rehydrated.blocks[0].id == block.id
        assert rehydrated.blocks[0].duration == Minutes(60)
        assert rehydrated.blocks[0].area_id == area_a
        assert rehydrated.blocks[0].notes == "deep work"

    def test_round_trip_day_vacio(self):
        original = Day(
            id=DayId.generate(),
            space_id=SpaceId.generate(),
            date=date(2026, 4, 10),
            blocks=[],
        )
        data = day_to_dict(original)
        rehydrated = day_from_dict(data)
        assert rehydrated.blocks == []

    def test_round_trip_block_sin_area(self):
        block = TimeBlock(
            id=BlockId.generate(),
            start_at=_ts(2026, 4, 10, 9),
            duration=Minutes(30),
            area_id=None,
            notes="",
        )
        original = Day(
            id=DayId.generate(),
            space_id=SpaceId.generate(),
            date=date(2026, 4, 10),
            blocks=[block],
        )
        rehydrated = day_from_dict(day_to_dict(original))
        assert rehydrated.blocks[0].area_id is None


# ── DayTemplate ───────────────────────────────────────────────────


class TestDayTemplateMapper:
    def test_round_trip_day_template(self):
        area_a = AreaId.generate()
        blocks = [
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=9, minute=0),
                duration=Minutes(60),
                area_id=area_a,
                notes="foco",
            ),
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=14, minute=30),
                duration=Minutes(30),
                area_id=None,
                notes="",
            ),
        ]
        original = DayTemplate(
            id=DayTemplateId.generate(),
            space_id=SpaceId.generate(),
            name="Día estándar",
            blocks=blocks,
        )

        data = day_template_to_dict(original)
        rehydrated = day_template_from_dict(data)

        assert rehydrated.id == original.id
        assert rehydrated.name == "Día estándar"
        assert len(rehydrated.blocks) == 2
        # Ordenados por start_at.to_minutes()
        assert rehydrated.blocks[0].start_at == TimeOfDay(hour=9, minute=0)
        assert rehydrated.blocks[1].start_at == TimeOfDay(hour=14, minute=30)
        assert rehydrated.blocks[0].area_id == area_a
        assert rehydrated.blocks[1].area_id is None

    def test_rehydratacion_no_modifica_updated_at(self):
        original_updated = Timestamp(
            datetime(2026, 4, 5, 10, 0, tzinfo=timezone.utc)
        )
        original = DayTemplate(
            id=DayTemplateId.generate(),
            space_id=SpaceId.generate(),
            name="Día estándar",
            blocks=[
                DayTemplateBlock(
                    id=BlockId.generate(),
                    start_at=TimeOfDay(hour=9, minute=0),
                    duration=Minutes(60),
                    area_id=None,
                )
            ],
            updated_at=original_updated,
        )

        data = day_template_to_dict(original)
        rehydrated = day_template_from_dict(data)

        # replace_blocks bumpearía updated_at; el mapper lo bypasea
        assert rehydrated.updated_at == original_updated

    def test_rehydrate_rechaza_bloques_solapados(self):
        """Datos corruptos en Firestore con bloques solapados no deben
        deserializarse silenciosamente — el mapper es el último guardián."""
        data = {
            "id": str(DayTemplateId.generate().value),
            "space_id": str(SpaceId.generate().value),
            "name": "Corrupto",
            "blocks": [
                {
                    "id": str(BlockId.generate().value),
                    "start_minutes": 540,  # 09:00
                    "duration": 120,  # hasta 11:00
                    "area_id": None,
                    "notes": "",
                },
                {
                    "id": str(BlockId.generate().value),
                    "start_minutes": 600,  # 10:00 (solapa con el anterior)
                    "duration": 60,
                    "area_id": None,
                    "notes": "",
                },
            ],
            "created_at": datetime(2026, 4, 5, 10, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 4, 5, 10, 0, tzinfo=timezone.utc),
        }
        with pytest.raises(BlockOverlapError):
            day_template_from_dict(data)

    def test_rehydrate_rechaza_bloques_con_wraparound(self):
        data = {
            "id": str(DayTemplateId.generate().value),
            "space_id": str(SpaceId.generate().value),
            "name": "Corrupto",
            "blocks": [
                {
                    "id": str(BlockId.generate().value),
                    "start_minutes": 1380,  # 23:00
                    "duration": 120,  # termina a las 25:00 → wraparound
                    "area_id": None,
                    "notes": "",
                },
            ],
            "created_at": datetime(2026, 4, 5, 10, 0, tzinfo=timezone.utc),
            "updated_at": datetime(2026, 4, 5, 10, 0, tzinfo=timezone.utc),
        }
        with pytest.raises(InvalidTimeBlockError):
            day_template_from_dict(data)


# ── WeekTemplate ──────────────────────────────────────────────────


class TestWeekTemplateMapper:
    def test_round_trip_week_template(self):
        dt_id_mon = DayTemplateId.generate()
        dt_id_wed = DayTemplateId.generate()
        slots: dict[DayOfWeek, DayTemplateId | None] = {
            DayOfWeek.MONDAY: dt_id_mon,
            DayOfWeek.TUESDAY: None,
            DayOfWeek.WEDNESDAY: dt_id_wed,
            DayOfWeek.THURSDAY: None,
            DayOfWeek.FRIDAY: None,
            DayOfWeek.SATURDAY: None,
            DayOfWeek.SUNDAY: None,
        }
        original = WeekTemplate(
            id=WeekTemplateId.generate(),
            space_id=SpaceId.generate(),
            name="Semana estándar",
            slots=slots,
        )

        data = week_template_to_dict(original)
        rehydrated = week_template_from_dict(data)

        assert rehydrated.id == original.id
        assert rehydrated.name == "Semana estándar"
        assert rehydrated.slots[DayOfWeek.MONDAY] == dt_id_mon
        assert rehydrated.slots[DayOfWeek.WEDNESDAY] == dt_id_wed
        assert rehydrated.slots[DayOfWeek.TUESDAY] is None
        assert rehydrated.slots[DayOfWeek.SUNDAY] is None

    def test_round_trip_week_template_vacio(self):
        original = WeekTemplate(
            id=WeekTemplateId.generate(),
            space_id=SpaceId.generate(),
            name="Vacía",
        )
        data = week_template_to_dict(original)
        rehydrated = week_template_from_dict(data)
        # WeekTemplate.__post_init__ rellena todos los slots a None
        assert all(v is None for v in rehydrated.slots.values())
        assert len(rehydrated.slots) == 7


# ── Week ──────────────────────────────────────────────────────────


class TestWeekMapper:
    def test_round_trip_week_vacio(self):
        space_id = SpaceId.generate()
        monday = date(2026, 4, 13)
        original = Week(
            id=WeekId.for_space_and_week_start(space_id, monday),
            space_id=space_id,
            week_start=monday,
        )

        data = week_to_dict(original)
        rehydrated = week_from_dict(data)

        assert rehydrated.id == original.id
        assert rehydrated.space_id == space_id
        assert rehydrated.week_start == monday
        assert rehydrated.notes == ""
        assert rehydrated.applied_template_id is None

    def test_round_trip_week_con_template_aplicado_y_notas(self):
        space_id = SpaceId.generate()
        monday = date(2026, 4, 13)
        wt_id = WeekTemplateId.generate()
        original = Week(
            id=WeekId.for_space_and_week_start(space_id, monday),
            space_id=space_id,
            week_start=monday,
            applied_template_id=wt_id,
            notes="Semana de foco profundo",
        )

        data = week_to_dict(original)
        rehydrated = week_from_dict(data)

        assert rehydrated.applied_template_id == wt_id
        assert rehydrated.notes == "Semana de foco profundo"
