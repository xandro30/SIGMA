"""Unit tests para WorkSession aggregate — state machine."""
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sigma_core.tracking.domain.aggregates.work_session import WorkSession, WorkSessionState
from sigma_core.tracking.domain.value_objects.ids import WorkSessionId
from sigma_core.tracking.domain.value_objects.timer import Timer, TimerTechnique
from sigma_core.tracking.domain.errors import InvalidWorkSessionTransitionError
from sigma_core.shared_kernel.events import WorkSessionCompleted
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, Timestamp

MADRID = ZoneInfo("Europe/Madrid")


def _ts(offset_minutes: int = 0) -> Timestamp:
    base = datetime(2026, 4, 14, 9, 0, tzinfo=MADRID)
    return Timestamp(base + timedelta(minutes=offset_minutes))


def _timer(num_rounds: int = 4) -> Timer:
    return Timer(
        technique=TimerTechnique.POMODORO,
        work_minutes=25,
        break_minutes=5,
        num_rounds=num_rounds,
    )


def _make_session(num_rounds: int = 4) -> WorkSession:
    return WorkSession(
        id=WorkSessionId.generate(),
        space_id=SpaceId.generate(),
        card_id=CardId.generate(),
        area_id=None,
        project_id=None,
        epic_id=None,
        description="Working on feature X",
        timer=_timer(num_rounds),
        completed_rounds=0,
        state=WorkSessionState.WORKING,
        session_started_at=_ts(0),
        current_started_at=_ts(0),
    )


# ── Estado inicial ────────────────────────────────────────────────

def test_new_session_state_is_working():
    s = _make_session()
    assert s.state == WorkSessionState.WORKING


def test_new_session_completed_rounds_is_zero():
    s = _make_session()
    assert s.completed_rounds == 0


def test_new_session_has_no_pending_events():
    s = _make_session()
    assert s.collect_events() == []


# ── complete_round ────────────────────────────────────────────────

def test_complete_round_increments_counter():
    s = _make_session(num_rounds=4)
    s.complete_round(_ts(25))
    assert s.completed_rounds == 1


def test_complete_round_transitions_to_break_when_more_rounds_remain():
    s = _make_session(num_rounds=4)
    s.complete_round(_ts(25))
    assert s.state == WorkSessionState.BREAK


def test_complete_round_updates_current_started_at():
    s = _make_session(num_rounds=4)
    now = _ts(25)
    s.complete_round(now)
    assert s.current_started_at == now


def test_complete_last_round_transitions_to_completed():
    s = _make_session(num_rounds=1)
    s.complete_round(_ts(25))
    assert s.state == WorkSessionState.COMPLETED


def test_complete_last_round_records_work_session_completed_event():
    s = _make_session(num_rounds=1)
    s.complete_round(_ts(25))
    events = s.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], WorkSessionCompleted)


def test_complete_last_round_event_contains_correct_minutes():
    s = _make_session(num_rounds=1)
    s.complete_round(_ts(25))
    event = s.collect_events()[0]
    assert event.minutes == 25


def test_complete_round_during_break_raises():
    s = _make_session(num_rounds=4)
    s.complete_round(_ts(25))  # → BREAK
    with pytest.raises(InvalidWorkSessionTransitionError):
        s.complete_round(_ts(30))


def test_complete_round_when_completed_raises():
    s = _make_session(num_rounds=1)
    s.complete_round(_ts(25))  # → COMPLETED
    with pytest.raises(InvalidWorkSessionTransitionError):
        s.complete_round(_ts(30))


# ── resume_from_break ─────────────────────────────────────────────

def test_resume_from_break_transitions_to_working():
    s = _make_session(num_rounds=4)
    s.complete_round(_ts(25))   # → BREAK
    s.resume_from_break(_ts(30))
    assert s.state == WorkSessionState.WORKING


def test_resume_from_break_updates_current_started_at():
    s = _make_session(num_rounds=4)
    s.complete_round(_ts(25))
    now = _ts(30)
    s.resume_from_break(now)
    assert s.current_started_at == now


def test_resume_from_working_raises():
    s = _make_session()
    with pytest.raises(InvalidWorkSessionTransitionError):
        s.resume_from_break(_ts(5))


# ── stop ──────────────────────────────────────────────────────────

def test_stop_with_save_transitions_to_completed():
    s = _make_session()
    s.stop(_ts(18), save=True)
    assert s.state == WorkSessionState.COMPLETED


def test_stop_with_save_records_event():
    s = _make_session()
    s.stop(_ts(18), save=True)
    events = s.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], WorkSessionCompleted)


def test_stop_with_save_event_minutes_is_elapsed_time():
    s = _make_session()
    s.stop(_ts(18), save=True)
    event = s.collect_events()[0]
    assert event.minutes == 18


def test_stop_without_save_transitions_to_stopped():
    s = _make_session()
    s.stop(_ts(18), save=False)
    assert s.state == WorkSessionState.STOPPED


def test_stop_without_save_records_no_event():
    s = _make_session()
    s.stop(_ts(18), save=False)
    assert s.collect_events() == []


def test_stop_already_completed_raises():
    s = _make_session(num_rounds=1)
    s.complete_round(_ts(25))
    with pytest.raises(InvalidWorkSessionTransitionError):
        s.stop(_ts(30), save=True)


def test_stop_already_stopped_raises():
    s = _make_session()
    s.stop(_ts(18), save=False)
    with pytest.raises(InvalidWorkSessionTransitionError):
        s.stop(_ts(20), save=False)


# ── event contents ────────────────────────────────────────────────

def test_event_contains_card_and_space_ids():
    s = _make_session()
    s.stop(_ts(10), save=True)
    event = s.collect_events()[0]
    assert event.card_id == s.card_id
    assert event.space_id == s.space_id
    assert event.description == s.description


def test_collect_events_clears_pending():
    s = _make_session()
    s.stop(_ts(10), save=True)
    s.collect_events()
    assert s.collect_events() == []
