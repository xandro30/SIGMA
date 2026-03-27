from datetime import date

from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, CardTitle,
)

from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.card_filter import (
    CardFilter, StringContains, StringEquals,
    ListHasAny, ListHasNone, DateBefore,
)


def make_card(**kwargs) -> Card:
    defaults = dict(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Tarea"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    defaults.update(kwargs)
    return Card(**defaults)


def test_empty_filter_matches_any_card():
    card = make_card()
    assert CardFilter().matches(card) is True


def test_filter_by_title_contains():
    card = make_card(title=CardTitle("Revisar logs de Chronicle"))
    assert CardFilter(title=StringContains("logs")).matches(card) is True
    assert CardFilter(title=StringContains("deploy")).matches(card) is False


def test_filter_by_priority():
    card = make_card(priority=Priority.HIGH)
    assert CardFilter(priority=[Priority.HIGH, Priority.CRITICAL]).matches(card) is True
    assert CardFilter(priority=[Priority.LOW]).matches(card) is False


def test_filter_by_labels_has_any():
    card = make_card(labels={"#SecOps", "#Work"})
    assert CardFilter(labels=ListHasAny(frozenset({"#SecOps"}))).matches(card) is True
    assert CardFilter(labels=ListHasAny(frozenset({"#Personal"}))).matches(card) is False


def test_filter_by_labels_has_none():
    card = make_card(labels={"#SecOps"})
    assert CardFilter(labels=ListHasNone(frozenset({"#Personal"}))).matches(card) is True
    assert CardFilter(labels=ListHasNone(frozenset({"#SecOps"}))).matches(card) is False


def test_filter_by_due_date_before():
    card = make_card(due_date=date(2026, 3, 20))
    assert CardFilter(due_date=DateBefore(date(2026, 4, 1))).matches(card) is True
    assert CardFilter(due_date=DateBefore(date(2026, 3, 1))).matches(card) is False


def test_multiple_filters_combined_with_and():
    card = make_card(priority=Priority.HIGH, labels={"#SecOps"})
    assert CardFilter(priority=[Priority.HIGH], labels=ListHasAny(frozenset({"#SecOps"})),).matches(card) is True
    assert CardFilter(priority=[Priority.LOW],labels=ListHasAny(frozenset({"#SecOps"})),).matches(card) is False