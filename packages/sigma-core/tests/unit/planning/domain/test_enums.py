from datetime import date

from sigma_core.planning.domain.enums import CycleState, DayOfWeek


# ── CycleState ───────────────────────────────────────────────────


def test_cycle_state_tiene_tres_valores():
    assert CycleState.DRAFT.value == "draft"
    assert CycleState.ACTIVE.value == "active"
    assert CycleState.CLOSED.value == "closed"


def test_cycle_state_se_construye_desde_string():
    assert CycleState("draft") == CycleState.DRAFT
    assert CycleState("active") == CycleState.ACTIVE
    assert CycleState("closed") == CycleState.CLOSED


def test_cycle_state_es_subclase_de_str():
    assert isinstance(CycleState.DRAFT, str)


# ── DayOfWeek ────────────────────────────────────────────────────


def test_day_of_week_usa_convencion_iso_lunes_cero():
    assert DayOfWeek.MONDAY.value == 0
    assert DayOfWeek.TUESDAY.value == 1
    assert DayOfWeek.WEDNESDAY.value == 2
    assert DayOfWeek.THURSDAY.value == 3
    assert DayOfWeek.FRIDAY.value == 4
    assert DayOfWeek.SATURDAY.value == 5
    assert DayOfWeek.SUNDAY.value == 6


def test_day_of_week_from_date_lunes():
    # 2026-04-13 es lunes
    assert DayOfWeek.from_date(date(2026, 4, 13)) == DayOfWeek.MONDAY


def test_day_of_week_from_date_domingo():
    # 2026-04-19 es domingo
    assert DayOfWeek.from_date(date(2026, 4, 19)) == DayOfWeek.SUNDAY


def test_day_of_week_from_date_miercoles():
    # 2026-04-15 es miércoles
    assert DayOfWeek.from_date(date(2026, 4, 15)) == DayOfWeek.WEDNESDAY


def test_day_of_week_es_iterable_con_los_siete_dias():
    days = list(DayOfWeek)
    assert len(days) == 7
    assert days[0] == DayOfWeek.MONDAY
    assert days[-1] == DayOfWeek.SUNDAY
