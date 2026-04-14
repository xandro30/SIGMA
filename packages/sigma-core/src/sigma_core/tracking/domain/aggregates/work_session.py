"""WorkSession aggregate — sesion activa de trabajo con state machine."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from sigma_core.shared_kernel.aggregate import EventEmitterMixin
from sigma_core.shared_kernel.events import WorkSessionCompleted
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId
from sigma_core.tracking.domain.errors import InvalidWorkSessionTransitionError
from sigma_core.tracking.domain.value_objects.ids import WorkSessionId
from sigma_core.tracking.domain.value_objects.timer import Timer


class WorkSessionState(Enum):
    WORKING = "working"
    BREAK = "break"
    COMPLETED = "completed"
    STOPPED = "stopped"


@dataclass
class WorkSession(EventEmitterMixin):
    """Sesion activa de trabajo. Una por space.

    State machine:
        WORKING → complete_round() → BREAK (rounds remain) | COMPLETED (last round)
        BREAK   → resume_from_break() → WORKING
        WORKING | BREAK → stop(save=True)  → COMPLETED  (emite WorkSessionCompleted)
        WORKING | BREAK → stop(save=False) → STOPPED
    """

    id: WorkSessionId
    space_id: SpaceId
    card_id: CardId
    area_id: AreaId | None
    project_id: ProjectId | None
    epic_id: EpicId | None
    description: str
    timer: Timer
    completed_rounds: int
    state: WorkSessionState
    session_started_at: Timestamp
    current_started_at: Timestamp

    def __post_init__(self) -> None:
        self._pending_events: list = []

    # ── State machine ──────────────────────────────────────────────

    def complete_round(self, now: Timestamp) -> None:
        if self.state != WorkSessionState.WORKING:
            raise InvalidWorkSessionTransitionError(
                f"Cannot complete round from state {self.state.value}"
            )
        self.completed_rounds += 1
        self.current_started_at = now

        if self.completed_rounds >= self.timer.num_rounds:
            self.state = WorkSessionState.COMPLETED
            self._record_event(self._make_completed_event(now))
        else:
            self.state = WorkSessionState.BREAK

    def resume_from_break(self, now: Timestamp) -> None:
        if self.state != WorkSessionState.BREAK:
            raise InvalidWorkSessionTransitionError(
                f"Cannot resume from state {self.state.value}"
            )
        self.state = WorkSessionState.WORKING
        self.current_started_at = now

    def stop(self, now: Timestamp, save: bool) -> None:
        if self.state in (WorkSessionState.COMPLETED, WorkSessionState.STOPPED):
            raise InvalidWorkSessionTransitionError(
                f"Cannot stop session already in state {self.state.value}"
            )
        if save:
            self.state = WorkSessionState.COMPLETED
            self._record_event(self._make_completed_event(now))
        else:
            self.state = WorkSessionState.STOPPED

    # ── Helpers ───────────────────────────────────────────────────

    def _make_completed_event(self, now: Timestamp) -> WorkSessionCompleted:
        elapsed = int(
            (now.value - self.session_started_at.value).total_seconds() / 60
        )
        return WorkSessionCompleted(
            occurred_at=now,
            space_id=self.space_id,
            card_id=self.card_id,
            area_id=self.area_id,
            project_id=self.project_id,
            epic_id=self.epic_id,
            description=self.description,
            minutes=elapsed,
        )
