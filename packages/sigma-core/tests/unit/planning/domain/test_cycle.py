from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from sigma_core.planning.domain.aggregates.cycle import Cycle
from sigma_core.planning.domain.enums import CycleState
from sigma_core.planning.domain.errors import (
    BudgetNotFoundError,
    InvalidBufferError,
    InvalidCycleTransitionError,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MADRID = ZoneInfo("Europe/Madrid")


def ts(h: int = 12, m: int = 0) -> Timestamp:
    return Timestamp(datetime(2026, 4, 11, h, m, tzinfo=MADRID))


def _range() -> DateRange:
    return DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))


def _new_cycle() -> Cycle:
    return Cycle(
        id=CycleId.generate(),
        space_id=SpaceId.generate(),
        name="April cycle",
        date_range=_range(),
    )


# ── Construcción ────────────────────────────────────────────────


def test_cycle_se_crea_en_estado_draft_con_defaults():
    cycle = _new_cycle()

    assert cycle.state == CycleState.DRAFT
    assert cycle.area_budgets == {}
    assert cycle.buffer_percentage == 20
    assert cycle.closed_at is None


def test_cycle_conserva_name_space_id_y_date_range():
    space_id = SpaceId.generate()
    cycle = Cycle(
        id=CycleId.generate(),
        space_id=space_id,
        name="Sprint 1",
        date_range=_range(),
    )

    assert cycle.name == "Sprint 1"
    assert cycle.space_id == space_id
    assert cycle.date_range == _range()


# ── activate ─────────────────────────────────────────────────────


def test_cycle_activate_transiciona_draft_a_active():
    cycle = _new_cycle()

    cycle.activate()

    assert cycle.state == CycleState.ACTIVE


def test_cycle_activate_bumpea_updated_at():
    cycle = _new_cycle()
    before = cycle.updated_at

    cycle.activate()

    assert cycle.updated_at.value >= before.value


def test_cycle_activate_rechaza_si_ya_activo():
    cycle = _new_cycle()
    cycle.activate()

    with pytest.raises(InvalidCycleTransitionError) as exc:
        cycle.activate()

    assert exc.value.from_state == CycleState.ACTIVE.value
    assert exc.value.to_state == CycleState.ACTIVE.value


def test_cycle_activate_rechaza_si_closed():
    cycle = _new_cycle()
    cycle.close(ts())

    with pytest.raises(InvalidCycleTransitionError):
        cycle.activate()


# ── close ───────────────────────────────────────────────────────


def test_cycle_close_transiciona_draft_a_closed():
    cycle = _new_cycle()
    now = ts()

    cycle.close(now)

    assert cycle.state == CycleState.CLOSED
    assert cycle.closed_at == now


def test_cycle_close_transiciona_active_a_closed():
    cycle = _new_cycle()
    cycle.activate()
    now = ts()

    cycle.close(now)

    assert cycle.state == CycleState.CLOSED
    assert cycle.closed_at == now


def test_cycle_close_rechaza_si_ya_closed():
    cycle = _new_cycle()
    cycle.close(ts())

    with pytest.raises(InvalidCycleTransitionError):
        cycle.close(ts())


# ── area budgets ────────────────────────────────────────────────


def test_cycle_set_area_budget_agrega_entrada():
    cycle = _new_cycle()
    area_id = AreaId.generate()

    cycle.set_area_budget(area_id, Minutes(600))

    assert cycle.area_budgets[area_id] == Minutes(600)


def test_cycle_set_area_budget_reemplaza_existente():
    cycle = _new_cycle()
    area_id = AreaId.generate()
    cycle.set_area_budget(area_id, Minutes(600))

    cycle.set_area_budget(area_id, Minutes(900))

    assert cycle.area_budgets[area_id] == Minutes(900)


def test_cycle_set_area_budget_rechaza_en_closed():
    cycle = _new_cycle()
    cycle.close(ts())

    with pytest.raises(InvalidCycleTransitionError):
        cycle.set_area_budget(AreaId.generate(), Minutes(600))


def test_cycle_remove_area_budget_quita_entrada():
    cycle = _new_cycle()
    area_id = AreaId.generate()
    cycle.set_area_budget(area_id, Minutes(600))

    cycle.remove_area_budget(area_id)

    assert area_id not in cycle.area_budgets


def test_cycle_remove_area_budget_sin_entrada_lanza_error():
    cycle = _new_cycle()

    with pytest.raises(BudgetNotFoundError):
        cycle.remove_area_budget(AreaId.generate())


def test_cycle_remove_area_budget_rechaza_en_closed():
    cycle = _new_cycle()
    area_id = AreaId.generate()
    cycle.set_area_budget(area_id, Minutes(600))
    cycle.close(ts())

    with pytest.raises(InvalidCycleTransitionError):
        cycle.remove_area_budget(area_id)


# ── buffer percentage ───────────────────────────────────────────


@pytest.mark.parametrize("value", [0, 1, 20, 50, 100])
def test_cycle_set_buffer_percentage_acepta_rango_valido(value):
    cycle = _new_cycle()

    cycle.set_buffer_percentage(value)

    assert cycle.buffer_percentage == value


@pytest.mark.parametrize("value", [-1, 101, -100, 200])
def test_cycle_set_buffer_percentage_rechaza_fuera_de_rango(value):
    cycle = _new_cycle()

    with pytest.raises(InvalidBufferError):
        cycle.set_buffer_percentage(value)


def test_cycle_set_buffer_percentage_rechaza_en_closed():
    cycle = _new_cycle()
    cycle.close(ts())

    with pytest.raises(InvalidCycleTransitionError):
        cycle.set_buffer_percentage(50)
