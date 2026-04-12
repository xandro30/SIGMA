from __future__ import annotations

from datetime import date
from enum import Enum


class CycleState(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class CycleType(str, Enum):
    """Tipo de ciclo. Puede haber un ciclo activo por tipo por Space."""

    SPRINT = "sprint"
    QUARTER = "quarter"
    SEMESTER = "semester"
    ANNUAL = "annual"


class DayOfWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def from_date(cls, d: date) -> DayOfWeek:
        return cls(d.weekday())
