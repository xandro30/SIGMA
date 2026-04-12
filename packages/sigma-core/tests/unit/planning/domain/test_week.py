"""Tests unit del agregado Week."""
from datetime import date

import pytest

from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.errors import InvalidWeekStartError
from sigma_core.planning.domain.value_objects import WeekId, WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


MONDAY = date(2026, 4, 13)


def _week(*, week_start: date = MONDAY) -> Week:
    space_id = SpaceId.generate()
    return Week(
        id=WeekId.for_space_and_week_start(space_id, week_start),
        space_id=space_id,
        week_start=week_start,
    )


class TestWeekConstruction:
    def test_crea_week_con_defaults_vacios(self):
        w = _week()
        assert w.week_start == MONDAY
        assert w.notes == ""
        assert w.applied_template_id is None

    @pytest.mark.parametrize(
        "wrong_day",
        [
            date(2026, 4, 12),  # domingo
            date(2026, 4, 14),  # martes
            date(2026, 4, 19),  # domingo siguiente
        ],
    )
    def test_rechaza_week_start_que_no_sea_lunes(self, wrong_day):
        space_id = SpaceId.generate()
        with pytest.raises(InvalidWeekStartError):
            Week(
                id=WeekId.for_space_and_week_start(space_id, wrong_day),
                space_id=space_id,
                week_start=wrong_day,
            )


class TestWeekNotes:
    def test_set_notes_guarda_y_bumpea_updated_at(self):
        w = _week()
        original_updated = w.updated_at
        w.set_notes("Semana dura, pocos interrupts.")
        assert w.notes == "Semana dura, pocos interrupts."
        assert w.updated_at != original_updated or w.updated_at >= original_updated

    def test_set_notes_acepta_string_vacio(self):
        w = _week()
        w.set_notes("algo")
        w.set_notes("")
        assert w.notes == ""


class TestWeekAppliedTemplate:
    def test_record_template_applied_guarda_referencia(self):
        w = _week()
        template_id = WeekTemplateId.generate()
        w.record_template_applied(template_id)
        assert w.applied_template_id == template_id

    def test_record_template_applied_sobrescribe_anterior(self):
        w = _week()
        t1 = WeekTemplateId.generate()
        t2 = WeekTemplateId.generate()
        w.record_template_applied(t1)
        w.record_template_applied(t2)
        assert w.applied_template_id == t2

    def test_clear_applied_template_pone_none(self):
        w = _week()
        w.record_template_applied(WeekTemplateId.generate())
        w.clear_applied_template()
        assert w.applied_template_id is None
