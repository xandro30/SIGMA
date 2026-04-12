from sigma_core.planning.domain.aggregates.week_template import WeekTemplate
from sigma_core.planning.domain.enums import DayOfWeek
from sigma_core.planning.domain.value_objects import DayTemplateId, WeekTemplateId
from sigma_core.shared_kernel.value_objects import SpaceId


def _template() -> WeekTemplate:
    return WeekTemplate(
        id=WeekTemplateId.generate(),
        space_id=SpaceId.generate(),
        name="Semana tipo",
    )


class TestWeekTemplate:
    def test_post_init_normaliza_7_slots_a_none(self):
        wt = _template()
        assert set(wt.slots.keys()) == set(DayOfWeek)
        assert all(v is None for v in wt.slots.values())

    def test_set_slot_asigna_day_template_id(self):
        wt = _template()
        template_id = DayTemplateId.generate()
        wt.set_slot(DayOfWeek.MONDAY, template_id)
        assert wt.slots[DayOfWeek.MONDAY] == template_id

    def test_clear_slot_pone_a_none(self):
        wt = _template()
        template_id = DayTemplateId.generate()
        wt.set_slot(DayOfWeek.MONDAY, template_id)
        wt.clear_slot(DayOfWeek.MONDAY)
        assert wt.slots[DayOfWeek.MONDAY] is None

    def test_rename_actualiza_nombre(self):
        wt = _template()
        wt.rename("Renombrado")
        assert wt.name == "Renombrado"
