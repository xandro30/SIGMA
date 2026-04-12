from __future__ import annotations

from dataclasses import dataclass, field

from sigma_core.planning.domain.enums import CycleState, CycleType
from sigma_core.planning.domain.errors import (
    BudgetNotFoundError,
    InvalidBufferError,
    InvalidCycleTransitionError,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.aggregate import EventEmitterMixin
from sigma_core.shared_kernel.events import CycleClosed
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MIN_BUFFER_PERCENTAGE = 0
MAX_BUFFER_PERCENTAGE = 100
DEFAULT_BUFFER_PERCENTAGE = 20


@dataclass
class Cycle(EventEmitterMixin):
    id: CycleId
    space_id: SpaceId
    name: str
    date_range: DateRange
    cycle_type: CycleType = CycleType.SPRINT
    state: CycleState = CycleState.DRAFT
    area_budgets: dict[AreaId, Minutes] = field(default_factory=dict)
    buffer_percentage: int = DEFAULT_BUFFER_PERCENTAGE
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    closed_at: Timestamp | None = None

    def __post_init__(self) -> None:
        self._pending_events = []

    # ── State machine ──────────────────────────────────────────

    def activate(self) -> None:
        if self.state != CycleState.DRAFT:
            raise InvalidCycleTransitionError(
                from_state=self.state.value,
                to_state=CycleState.ACTIVE.value,
            )
        self.state = CycleState.ACTIVE
        self._touch()

    def close(self, now: Timestamp) -> None:
        if self.state == CycleState.CLOSED:
            raise InvalidCycleTransitionError(
                from_state=self.state.value,
                to_state=CycleState.CLOSED.value,
            )
        self.state = CycleState.CLOSED
        self.closed_at = now
        self._touch()
        self._record_event(
            CycleClosed(
                occurred_at=now,
                cycle_id=self.id,
                space_id=self.space_id,
                date_range=self.date_range,
            )
        )

    # ── Area budgets ───────────────────────────────────────────

    def set_area_budget(self, area_id: AreaId, minutes: Minutes) -> None:
        self._ensure_mutable()
        self.area_budgets[area_id] = minutes
        self._touch()

    def remove_area_budget(self, area_id: AreaId) -> None:
        self._ensure_mutable()
        if area_id not in self.area_budgets:
            raise BudgetNotFoundError(
                f"Area {area_id.value} has no budget in cycle {self.id.value}"
            )
        del self.area_budgets[area_id]
        self._touch()

    # ── Buffer percentage ──────────────────────────────────────

    def set_buffer_percentage(self, value: int) -> None:
        self._ensure_mutable()
        if not MIN_BUFFER_PERCENTAGE <= value <= MAX_BUFFER_PERCENTAGE:
            raise InvalidBufferError(
                f"buffer_percentage must be in "
                f"{MIN_BUFFER_PERCENTAGE}..{MAX_BUFFER_PERCENTAGE}, got {value}"
            )
        self.buffer_percentage = value
        self._touch()

    # ── Internal helpers ───────────────────────────────────────

    def _ensure_mutable(self) -> None:
        if self.state == CycleState.CLOSED:
            raise InvalidCycleTransitionError(
                from_state=self.state.value,
                to_state=self.state.value,
            )

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
