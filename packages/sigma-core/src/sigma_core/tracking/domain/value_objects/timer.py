"""Timer value object — tecnica de concentracion y su configuracion."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TimerTechnique(Enum):
    POMODORO = "pomodoro"


@dataclass(frozen=True)
class Timer:
    """Encapsula la tecnica de concentracion y su configuracion.

    Hoy solo soporta Pomodoro. Extensible a DeepWork, Flowtime, etc.
    sin modificar WorkSession.
    """

    technique: TimerTechnique
    work_minutes: int
    break_minutes: int
    num_rounds: int

    def __post_init__(self) -> None:
        if self.work_minutes <= 0:
            raise ValueError("work_minutes must be positive")
        if self.break_minutes < 0:
            raise ValueError("break_minutes must be >= 0")
        if self.num_rounds <= 0:
            raise ValueError("num_rounds must be positive")

    @property
    def total_work_minutes(self) -> int:
        return self.work_minutes * self.num_rounds
