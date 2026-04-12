import pytest

from sigma_core.planning.domain.aggregates.day_template import DayTemplate
from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    InvalidTimeBlockError,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import Minutes, SpaceId


def tpl_block(
    hour: int,
    minute: int = 0,
    duration: int = 60,
    notes: str = "",
) -> DayTemplateBlock:
    return DayTemplateBlock(
        id=BlockId.generate(),
        start_at=TimeOfDay(hour=hour, minute=minute),
        duration=Minutes(duration),
        area_id=None,
        notes=notes,
    )


def _empty_template() -> DayTemplate:
    return DayTemplate(
        id=DayTemplateId.generate(),
        space_id=SpaceId.generate(),
        name="Lunes tipo",
    )


class TestDayTemplateBlock:
    def test_end_minutes_es_start_mas_duration(self):
        b = tpl_block(hour=9, minute=15, duration=45)
        assert b.end_minutes() == 9 * 60 + 15 + 45

    def test_duration_cero_rechazada(self):
        with pytest.raises(InvalidTimeBlockError):
            DayTemplateBlock(
                id=BlockId.generate(),
                start_at=TimeOfDay(hour=9, minute=0),
                duration=Minutes(0),
                area_id=None,
            )


class TestDayTemplateMutations:
    def test_add_block_ordena_por_start(self):
        template = _empty_template()
        b1 = tpl_block(hour=10)
        b2 = tpl_block(hour=9)
        template.add_block(b1)
        template.add_block(b2)
        assert [b.id for b in template.blocks] == [b2.id, b1.id]

    def test_add_block_rechaza_solapamiento(self):
        template = _empty_template()
        template.add_block(tpl_block(hour=9, duration=60))
        with pytest.raises(BlockOverlapError):
            template.add_block(tpl_block(hour=9, minute=30, duration=30))

    def test_add_block_rechaza_wraparound(self):
        template = _empty_template()
        with pytest.raises(InvalidTimeBlockError):
            template.add_block(tpl_block(hour=23, minute=30, duration=60))

    def test_remove_block_lo_elimina(self):
        template = _empty_template()
        b = tpl_block(hour=9)
        template.add_block(b)
        template.remove_block(b.id)
        assert template.blocks == []

    def test_remove_block_inexistente_falla(self):
        template = _empty_template()
        with pytest.raises(BlockNotFoundError):
            template.remove_block(BlockId.generate())

    def test_update_block_reemplaza_campos(self):
        template = _empty_template()
        b = tpl_block(hour=9, notes="old")
        template.add_block(b)
        template.update_block(
            b.id,
            start_at=TimeOfDay(hour=10, minute=0),
            duration=Minutes(30),
            notes="new",
        )
        updated = template.blocks[0]
        assert updated.start_at == TimeOfDay(hour=10, minute=0)
        assert updated.duration == Minutes(30)
        assert updated.notes == "new"

    def test_update_block_rechaza_solapamiento_con_otro(self):
        template = _empty_template()
        b1 = tpl_block(hour=9, duration=60)
        b2 = tpl_block(hour=11, duration=60)
        template.add_block(b1)
        template.add_block(b2)
        with pytest.raises(BlockOverlapError):
            template.update_block(b2.id, start_at=TimeOfDay(hour=9, minute=30))

    def test_clear_blocks_vacia_lista(self):
        template = _empty_template()
        template.add_block(tpl_block(hour=9))
        template.add_block(tpl_block(hour=11))
        template.clear_blocks()
        assert template.blocks == []
