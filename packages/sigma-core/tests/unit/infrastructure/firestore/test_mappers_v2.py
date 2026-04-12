import pytest

from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import Space
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import PreWorkflowStage
from sigma_core.shared_kernel.value_objects import (
    CardId,
    Minutes,
    SizeMapping,
    SpaceId,
    Timestamp,
)
from sigma_core.task_management.domain.value_objects import CardTitle, SpaceName
from sigma_core.task_management.infrastructure.firestore.mappers import (
    card_from_dict,
    card_to_dict,
    space_from_dict,
    space_to_dict,
)
from tests.helpers.timestamps import ts as _ts


def _make_card(
    size: CardSize | None = None,
    actual_time: Minutes | None = None,
    timer_started_at: Timestamp | None = None,
    completed_at: Timestamp | None = None,
) -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card"),
        pre_workflow_stage=PreWorkflowStage.BACKLOG,
        workflow_state_id=None,
        size=size,
        actual_time=actual_time if actual_time is not None else Minutes(0),
        timer_started_at=timer_started_at,
        completed_at=completed_at,
    )


def _make_space(size_mapping: SizeMapping | None = None) -> Space:
    return Space(
        id=SpaceId.generate(),
        name=SpaceName("Test space"),
        workflow_states=[],
        transitions=[],
        size_mapping=size_mapping,
    )


# ── Card v2 round-trip ───────────────────────────────────────────


def test_card_to_dict_incluye_campos_v2_por_defecto():
    card = _make_card()

    data = card_to_dict(card)

    assert data["size"] is None
    assert data["actual_time"] == 0
    assert data["timer_started_at"] is None


def test_card_to_dict_serializa_size_asignado():
    card = _make_card(size=CardSize.M)

    data = card_to_dict(card)

    assert data["size"] == "m"


def test_card_to_dict_serializa_actual_time():
    card = _make_card(actual_time=Minutes(135))

    data = card_to_dict(card)

    assert data["actual_time"] == 135


def test_card_to_dict_serializa_timer_started_at():
    started = _ts(hour=9)
    card = _make_card(timer_started_at=started)

    data = card_to_dict(card)

    assert data["timer_started_at"] == started.value


def test_card_round_trip_con_campos_v2_nulos():
    card = _make_card()

    restored = card_from_dict(card_to_dict(card))

    assert restored.size is None
    assert restored.actual_time == Minutes(0)
    assert restored.timer_started_at is None
    assert restored.completed_at is None


def test_card_round_trip_con_campos_v2_poblados():
    started = _ts(hour=9)
    completed = _ts(hour=18)
    card = _make_card(
        size=CardSize.L,
        actual_time=Minutes(240),
        timer_started_at=started,
        completed_at=completed,
    )

    restored = card_from_dict(card_to_dict(card))

    assert restored.size == CardSize.L
    assert restored.actual_time == Minutes(240)
    assert restored.timer_started_at is not None
    assert restored.timer_started_at.value == started.value
    assert restored.completed_at is not None
    assert restored.completed_at.value == completed.value


def test_card_to_dict_serializa_completed_at_none_por_defecto():
    card = _make_card()

    data = card_to_dict(card)

    assert data["completed_at"] is None


def test_card_to_dict_serializa_completed_at_poblado():
    completed = _ts(hour=18)
    card = _make_card(completed_at=completed)

    data = card_to_dict(card)

    assert data["completed_at"] == completed.value


def test_card_from_dict_sin_completed_at_falla_fast():
    data = card_to_dict(_make_card())
    del data["completed_at"]

    with pytest.raises(KeyError):
        card_from_dict(data)


# ── Space v2 round-trip ──────────────────────────────────────────


def test_space_to_dict_sin_size_mapping_es_none():
    space = _make_space()

    data = space_to_dict(space)

    assert data["size_mapping"] is None


def test_space_to_dict_serializa_size_mapping_completo():
    space = _make_space(size_mapping=SizeMapping.default())

    data = space_to_dict(space)

    assert data["size_mapping"] == {
        "xxs": 60,
        "xs": 120,
        "s": 240,
        "m": 480,
        "l": 960,
        "xl": 1920,
        "xxl": 3840,
    }


def test_space_round_trip_sin_size_mapping():
    space = _make_space()

    restored = space_from_dict(space_to_dict(space))

    assert restored.size_mapping is None


def test_space_round_trip_con_size_mapping():
    mapping = SizeMapping.default()
    space = _make_space(size_mapping=mapping)

    restored = space_from_dict(space_to_dict(space))

    assert restored.size_mapping is not None
    assert restored.size_mapping.get_minutes(CardSize.M) == Minutes(480)
    assert restored.size_mapping.get_minutes(CardSize.XXL) == Minutes(3840)


# ── T6 strict schema (ADR-003 reset de datos en v2) ─────────────
#
# Los mappers v2 NO admiten documentos legacy pre-v2: la lectura de un
# documento sin los campos v2 debe fallar con KeyError de forma explícita.
# Esto está garantizado por el reset de datos en cada deploy v2.


def test_card_from_dict_sin_campos_v2_falla_fast():
    data = card_to_dict(_make_card())
    del data["size"]

    with pytest.raises(KeyError):
        card_from_dict(data)


def test_card_from_dict_sin_actual_time_falla_fast():
    data = card_to_dict(_make_card())
    del data["actual_time"]

    with pytest.raises(KeyError):
        card_from_dict(data)


def test_card_from_dict_sin_timer_started_at_falla_fast():
    data = card_to_dict(_make_card())
    del data["timer_started_at"]

    with pytest.raises(KeyError):
        card_from_dict(data)


def test_space_from_dict_sin_size_mapping_falla_fast():
    data = space_to_dict(_make_space())
    del data["size_mapping"]

    with pytest.raises(KeyError):
        space_from_dict(data)
