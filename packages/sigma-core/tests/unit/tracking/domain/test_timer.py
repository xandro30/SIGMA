"""Unit tests para Timer value object."""
import pytest

from sigma_core.tracking.domain.value_objects.timer import Timer, TimerTechnique


def _pomodoro(work_minutes: int = 25, break_minutes: int = 5, num_rounds: int = 4) -> Timer:
    return Timer(
        technique=TimerTechnique.POMODORO,
        work_minutes=work_minutes,
        break_minutes=break_minutes,
        num_rounds=num_rounds,
    )


# ── Construccion ──────────────────────────────────────────────────


def test_timer_stores_technique():
    t = _pomodoro()
    assert t.technique == TimerTechnique.POMODORO


def test_timer_stores_config():
    t = _pomodoro(work_minutes=50, break_minutes=10, num_rounds=2)
    assert t.work_minutes == 50
    assert t.break_minutes == 10
    assert t.num_rounds == 2


def test_timer_total_work_minutes():
    t = _pomodoro(work_minutes=25, num_rounds=4)
    assert t.total_work_minutes == 100


def test_timer_is_immutable():
    t = _pomodoro()
    with pytest.raises(Exception):
        t.work_minutes = 99  # type: ignore[misc]


# ── Validaciones ──────────────────────────────────────────────────


def test_timer_zero_rounds_raises():
    with pytest.raises(ValueError, match="num_rounds"):
        _pomodoro(num_rounds=0)


def test_timer_zero_work_minutes_raises():
    with pytest.raises(ValueError, match="work_minutes"):
        _pomodoro(work_minutes=0)


def test_timer_negative_break_minutes_raises():
    with pytest.raises(ValueError, match="break_minutes"):
        _pomodoro(break_minutes=-1)


# ── Tecnica ───────────────────────────────────────────────────────


def test_timer_technique_value():
    assert TimerTechnique.POMODORO.value == "pomodoro"
