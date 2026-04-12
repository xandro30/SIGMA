from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.domain.aggregates.day import MAX_BLOCKS_PER_DAY, Day
from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    InvalidTimeBlockError,
)
from sigma_core.planning.domain.value_objects import BlockId, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MADRID = ZoneInfo("Europe/Madrid")


def at(hour: int, minute: int = 0, day: date = date(2026, 4, 13)) -> Timestamp:
    return Timestamp(datetime(day.year, day.month, day.day, hour, minute, tzinfo=MADRID))


def block(
    hour: int,
    minute: int = 0,
    duration: int = 60,
    day: date = date(2026, 4, 13),
    area_id: AreaId | None = None,
    notes: str = "",
) -> TimeBlock:
    return TimeBlock(
        id=BlockId.generate(),
        start_at=at(hour, minute, day),
        duration=Minutes(duration),
        area_id=area_id,
        notes=notes,
    )


def _empty_day(d: date = date(2026, 4, 13)) -> Day:
    return Day(
        id=DayId.generate(),
        space_id=SpaceId.generate(),
        date=d,
    )


# ── TimeBlock entity ─────────────────────────────────────────────


class TestTimeBlock:
    def test_end_at_es_start_mas_duration(self):
        b = block(hour=9, minute=0, duration=90)
        assert b.end_at.value == at(10, 30).value

    def test_overlap_detecta_solapamiento(self):
        a = block(hour=9, duration=60)
        b = block(hour=9, minute=30, duration=60)
        assert a.overlaps(b) is True
        assert b.overlaps(a) is True

    def test_overlap_permite_contiguos(self):
        a = block(hour=9, duration=60)
        b = block(hour=10, duration=60)
        assert a.overlaps(b) is False
        assert b.overlaps(a) is False

    def test_overlap_detecta_contenido(self):
        outer = block(hour=9, duration=180)
        inner = block(hour=10, duration=30)
        assert outer.overlaps(inner) is True
        assert inner.overlaps(outer) is True

    def test_duration_cero_rechazada(self):
        with pytest.raises(InvalidTimeBlockError):
            TimeBlock(
                id=BlockId.generate(),
                start_at=at(9),
                duration=Minutes(0),
                area_id=None,
            )


# ── Day aggregate ───────────────────────────────────────────────


class TestDayAddBlock:
    def test_add_block_persiste_en_orden(self):
        day = _empty_day()
        b1 = block(hour=10)
        b2 = block(hour=9)
        day.add_block(b1)
        day.add_block(b2)
        assert [b.id for b in day.blocks] == [b2.id, b1.id]

    def test_add_block_rechaza_solapamiento(self):
        day = _empty_day()
        day.add_block(block(hour=9, duration=60))
        with pytest.raises(BlockOverlapError):
            day.add_block(block(hour=9, minute=30, duration=30))

    def test_add_block_rechaza_fecha_diferente(self):
        day = _empty_day(date(2026, 4, 13))
        other_day_block = block(hour=9, day=date(2026, 4, 14))
        with pytest.raises(InvalidTimeBlockError):
            day.add_block(other_day_block)

    def test_add_block_bumpea_updated_at(self):
        day = _empty_day()
        original = day.updated_at
        day.add_block(block(hour=9))
        assert day.updated_at.value >= original.value

    def test_add_block_rechaza_cuando_alcanza_cap(self):
        day = _empty_day()
        for i in range(MAX_BLOCKS_PER_DAY):
            hour = (i * 15) // 60
            minute = (i * 15) % 60
            day.add_block(block(hour=hour, minute=minute, duration=15))
        # Intentar añadir uno más debe fallar por cap
        extra = TimeBlock(
            id=BlockId.generate(),
            start_at=at(12, 5),
            duration=Minutes(5),
            area_id=None,
        )
        with pytest.raises(InvalidTimeBlockError):
            day.add_block(extra)


class TestDayRemoveBlock:
    def test_remove_block_lo_elimina(self):
        day = _empty_day()
        b = block(hour=9)
        day.add_block(b)
        day.remove_block(b.id)
        assert day.blocks == []

    def test_remove_block_no_existente_falla(self):
        day = _empty_day()
        with pytest.raises(BlockNotFoundError):
            day.remove_block(BlockId.generate())


class TestDayUpdateBlock:
    def test_update_block_reemplaza_campos(self):
        day = _empty_day()
        b = block(hour=9, duration=60, notes="old")
        day.add_block(b)
        day.update_block(
            b.id,
            start_at=at(10),
            duration=Minutes(30),
            notes="new",
        )
        updated = day.blocks[0]
        assert updated.start_at.value == at(10).value
        assert updated.duration == Minutes(30)
        assert updated.notes == "new"

    def test_update_block_check_solapamiento_excluyendo_el_mismo(self):
        day = _empty_day()
        b1 = block(hour=9, duration=60)
        b2 = block(hour=11, duration=60)
        day.add_block(b1)
        day.add_block(b2)
        # Mover b2 a las 10 (contiguo con b1) → sin solapamiento
        day.update_block(b2.id, start_at=at(10))
        assert day.blocks[1].start_at.value == at(10).value

    def test_update_block_rechaza_si_solapa_con_otro(self):
        day = _empty_day()
        b1 = block(hour=9, duration=60)
        b2 = block(hour=11, duration=60)
        day.add_block(b1)
        day.add_block(b2)
        with pytest.raises(BlockOverlapError):
            day.update_block(b2.id, start_at=at(9, 30))

    def test_update_block_no_existente_falla(self):
        day = _empty_day()
        with pytest.raises(BlockNotFoundError):
            day.update_block(BlockId.generate(), notes="x")


class TestDayClearBlocks:
    def test_clear_blocks_vacia_lista(self):
        day = _empty_day()
        day.add_block(block(hour=9))
        day.add_block(block(hour=10))
        day.clear_blocks()
        assert day.blocks == []
