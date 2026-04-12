from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from sigma_core.planning.domain.errors import InvalidDateRangeError
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
from sigma_core.shared_kernel.value_objects import SpaceId


# ── IDs ──────────────────────────────────────────────────────────

VALID_UUID = "11111111-1111-4111-a111-111111111111"

# DayId queda fuera de los parametrize genéricos porque acepta v4 y v5
# (ver tests específicos en la sección `DayId determinista`).
_STRICT_V4_IDS = [CycleId, DayTemplateId, WeekTemplateId, BlockId]


@pytest.mark.parametrize("id_cls", _STRICT_V4_IDS + [DayId])
def test_ids_aceptan_uuid_v4_valido(id_cls):
    instance = id_cls(VALID_UUID)
    assert instance.value == VALID_UUID


@pytest.mark.parametrize("id_cls", _STRICT_V4_IDS + [DayId])
def test_ids_rechazan_uuid_invalido(id_cls):
    with pytest.raises(ValueError):
        id_cls("not-a-uuid")


@pytest.mark.parametrize("id_cls", _STRICT_V4_IDS)
def test_ids_estrictos_rechazan_uuid_de_otra_version(id_cls):
    # UUID v1 (no v4)
    with pytest.raises(ValueError):
        id_cls("550e8400-e29b-11d4-a716-446655440000")


@pytest.mark.parametrize("id_cls", _STRICT_V4_IDS + [DayId])
def test_ids_generate_crea_uuid_reparseable(id_cls):
    instance = id_cls.generate()
    # debe ser re-parseable
    assert id_cls(instance.value) == instance


# ── DayId determinista ──────────────────────────────────────────

def test_day_id_acepta_uuid_v5():
    # UUID v5 pre-calculado (el VO debe aceptar v4 y v5)
    v5_uuid = "886313e1-3b8a-5372-9b90-0c9aee199e5d"
    instance = DayId(v5_uuid)
    assert instance.value == v5_uuid


def test_day_id_for_space_and_date_es_determinista():
    space_id = SpaceId.generate()
    target = date(2026, 4, 13)
    a = DayId.for_space_and_date(space_id, target)
    b = DayId.for_space_and_date(space_id, target)
    assert a == b


def test_day_id_for_space_and_date_distinto_por_space():
    target = date(2026, 4, 13)
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()
    assert DayId.for_space_and_date(space_a, target) != DayId.for_space_and_date(
        space_b, target
    )


def test_day_id_for_space_and_date_distinto_por_fecha():
    space_id = SpaceId.generate()
    assert DayId.for_space_and_date(
        space_id, date(2026, 4, 13)
    ) != DayId.for_space_and_date(space_id, date(2026, 4, 14))


def test_day_id_for_space_and_date_produce_valor_reparseable():
    space_id = SpaceId.generate()
    generated = DayId.for_space_and_date(space_id, date(2026, 4, 13))
    # El valor producido debe pasar la validación del propio VO
    assert DayId(generated.value) == generated


# ── WeekId determinista ─────────────────────────────────────────

def test_week_id_acepta_uuid_v5():
    v5_uuid = "886313e1-3b8a-5372-9b90-0c9aee199e5d"
    assert WeekId(v5_uuid).value == v5_uuid


def test_week_id_for_space_and_week_start_es_determinista():
    space_id = SpaceId.generate()
    monday = date(2026, 4, 13)
    a = WeekId.for_space_and_week_start(space_id, monday)
    b = WeekId.for_space_and_week_start(space_id, monday)
    assert a == b


def test_week_id_for_space_and_week_start_distinto_por_space():
    monday = date(2026, 4, 13)
    space_a = SpaceId.generate()
    space_b = SpaceId.generate()
    assert WeekId.for_space_and_week_start(
        space_a, monday
    ) != WeekId.for_space_and_week_start(space_b, monday)


def test_week_id_for_space_and_week_start_distinto_por_fecha():
    space_id = SpaceId.generate()
    assert WeekId.for_space_and_week_start(
        space_id, date(2026, 4, 13)
    ) != WeekId.for_space_and_week_start(space_id, date(2026, 4, 20))


def test_week_id_for_space_and_week_start_produce_valor_reparseable():
    space_id = SpaceId.generate()
    generated = WeekId.for_space_and_week_start(space_id, date(2026, 4, 13))
    assert WeekId(generated.value) == generated


def test_week_id_tiene_namespace_distinto_de_day_id():
    """Aunque WeekId y DayId usen la misma semilla (space_id + date ISO),
    sus namespaces UUID deben ser distintos para evitar colisiones entre
    los dos tipos."""
    space_id = SpaceId.generate()
    same_date = date(2026, 4, 13)
    week = WeekId.for_space_and_week_start(space_id, same_date)
    day = DayId.for_space_and_date(space_id, same_date)
    assert week.value != day.value


@pytest.mark.parametrize(
    "id_cls",
    [CycleId, DayId, DayTemplateId, WeekTemplateId, BlockId],
)
def test_ids_son_frozen(id_cls):
    instance = id_cls(VALID_UUID)
    with pytest.raises(FrozenInstanceError):
        instance.value = "otro"  # type: ignore[misc]


def test_ids_son_iguales_por_valor():
    assert CycleId(VALID_UUID) == CycleId(VALID_UUID)


def test_ids_distintos_no_son_iguales_entre_tipos():
    # DateRange y CycleId con el mismo UUID son tipos distintos
    assert CycleId(VALID_UUID) != DayId(VALID_UUID)


# ── DateRange ────────────────────────────────────────────────────


def test_date_range_valido_start_menor_que_end():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))
    assert r.start == date(2026, 4, 1)
    assert r.end == date(2026, 4, 30)


def test_date_range_valido_start_igual_end():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 1))
    assert r.days_count() == 1


def test_date_range_rechaza_start_mayor_que_end():
    with pytest.raises(InvalidDateRangeError):
        DateRange(start=date(2026, 4, 30), end=date(2026, 4, 1))


def test_date_range_contains_incluye_extremos():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))
    assert r.contains(date(2026, 4, 1)) is True
    assert r.contains(date(2026, 4, 30)) is True
    assert r.contains(date(2026, 4, 15)) is True


def test_date_range_contains_excluye_fuera_de_rango():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))
    assert r.contains(date(2026, 3, 31)) is False
    assert r.contains(date(2026, 5, 1)) is False


def test_date_range_days_count_inclusivo():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 7))
    assert r.days_count() == 7


def test_date_range_es_frozen():
    r = DateRange(start=date(2026, 4, 1), end=date(2026, 4, 30))
    with pytest.raises(FrozenInstanceError):
        r.start = date(2026, 4, 2)  # type: ignore[misc]


# ── TimeOfDay ────────────────────────────────────────────────────


def test_time_of_day_valido():
    t = TimeOfDay(hour=9, minute=30)
    assert t.hour == 9
    assert t.minute == 30


def test_time_of_day_medianoche():
    t = TimeOfDay(hour=0, minute=0)
    assert t.to_minutes() == 0


def test_time_of_day_ultimo_minuto_del_dia():
    t = TimeOfDay(hour=23, minute=59)
    assert t.to_minutes() == 23 * 60 + 59


def test_time_of_day_to_minutes():
    t = TimeOfDay(hour=9, minute=30)
    assert t.to_minutes() == 570


@pytest.mark.parametrize("hour", [-1, 24, 25, 100])
def test_time_of_day_rechaza_hora_fuera_de_rango(hour):
    with pytest.raises(ValueError):
        TimeOfDay(hour=hour, minute=0)


@pytest.mark.parametrize("minute", [-1, 60, 61, 100])
def test_time_of_day_rechaza_minuto_fuera_de_rango(minute):
    with pytest.raises(ValueError):
        TimeOfDay(hour=9, minute=minute)


def test_time_of_day_es_frozen():
    t = TimeOfDay(hour=9, minute=30)
    with pytest.raises(FrozenInstanceError):
        t.hour = 10  # type: ignore[misc]


def test_time_of_day_es_comparable_por_valor():
    assert TimeOfDay(hour=9, minute=30) == TimeOfDay(hour=9, minute=30)
    assert TimeOfDay(hour=9, minute=30) != TimeOfDay(hour=9, minute=31)
