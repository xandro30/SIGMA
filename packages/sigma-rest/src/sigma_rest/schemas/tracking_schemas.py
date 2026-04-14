"""Schemas Pydantic para el BC tracking."""
from typing import Literal

from pydantic import BaseModel, field_validator


# ── Request schemas ───────────────────────────────────────────────

class TimerRequest(BaseModel):
    technique: Literal["pomodoro"] = "pomodoro"
    work_minutes: int = 25
    break_minutes: int = 5
    num_rounds: int = 4

    @field_validator("work_minutes", "num_rounds")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("break_minutes")
    @classmethod
    def must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be >= 0")
        return v


class StartWorkSessionRequest(BaseModel):
    card_id: str
    area_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str
    timer: TimerRequest = TimerRequest()


# ── Response schemas ──────────────────────────────────────────────

class TimerResponse(BaseModel):
    technique: str
    work_minutes: int
    break_minutes: int
    num_rounds: int


class WorkSessionResponse(BaseModel):
    id: str
    space_id: str
    card_id: str
    area_id: str | None = None
    project_id: str | None = None
    epic_id: str | None = None
    description: str
    timer: TimerResponse
    completed_rounds: int
    state: str
    session_started_at: str
    current_started_at: str
