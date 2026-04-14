"""Tests para Card.add_work_log() y WorkLogEntry."""
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import BEGIN_STATE_ID
from sigma_core.task_management.domain.value_objects import CardTitle, WorkLogEntry
from sigma_core.shared_kernel.value_objects import CardId, Minutes, SpaceId, Timestamp


def _make_card() -> Card:
    return Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )


def _entry(log: str = "Worked on feature", minutes: int = 25) -> WorkLogEntry:
    return WorkLogEntry(log=log, minutes=minutes, logged_at=Timestamp.now())


# ── WorkLogEntry ──────────────────────────────────────────────────


def test_work_log_entry_stores_fields():
    ts = Timestamp.now()
    entry = WorkLogEntry(log="Did stuff", minutes=50, logged_at=ts)
    assert entry.log == "Did stuff"
    assert entry.minutes == 50
    assert entry.logged_at == ts


def test_work_log_entry_is_immutable():
    import pytest
    entry = _entry()
    with pytest.raises(Exception):
        entry.minutes = 99  # type: ignore[misc]


# ── Card.work_log initial state ───────────────────────────────────


def test_new_card_has_empty_work_log():
    card = _make_card()
    assert card.work_log == []


# ── Card.add_work_log ─────────────────────────────────────────────


def test_add_work_log_appends_entry():
    card = _make_card()
    entry = _entry()
    card.add_work_log(entry)
    assert len(card.work_log) == 1
    assert card.work_log[0] == entry


def test_add_work_log_accumulates_actual_time():
    card = _make_card()
    card.add_work_log(_entry(minutes=25))
    card.add_work_log(_entry(minutes=30))
    assert card.actual_time == Minutes(55)


def test_add_work_log_multiple_entries_all_preserved():
    card = _make_card()
    e1 = _entry(log="First session", minutes=25)
    e2 = _entry(log="Second session", minutes=50)
    card.add_work_log(e1)
    card.add_work_log(e2)
    assert len(card.work_log) == 2
    assert card.work_log[0] == e1
    assert card.work_log[1] == e2


def test_add_work_log_updates_updated_at():
    card = _make_card()
    before = card.updated_at
    card.add_work_log(_entry())
    assert card.updated_at.value >= before.value


def test_add_work_log_does_not_affect_existing_actual_time_from_timer():
    """actual_time acumulado por timer y por work_log se suman."""
    card = _make_card()
    card.actual_time = Minutes(10)  # simula tiempo previo de timer
    card.add_work_log(_entry(minutes=25))
    assert card.actual_time == Minutes(35)
