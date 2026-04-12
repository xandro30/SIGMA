"""Value objects del BC metrics."""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    CardId,
    SpaceId,
    Timestamp,
)
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


# ── Identifier helpers ────────────────────────────────────────────


def _validate_uuid4(value: str, class_name: str) -> None:
    try:
        parsed = uuid.UUID(value, version=4)
        if str(parsed) != value:
            raise ValueError()
    except ValueError:
        raise ValueError(f"{class_name} inválido: {value!r}")


# ── IDs ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CycleSummaryId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "CycleSummaryId")

    @classmethod
    def generate(cls) -> CycleSummaryId:
        return cls(str(uuid.uuid4()))


@dataclass(frozen=True)
class CycleSnapshotId:
    value: str

    def __post_init__(self) -> None:
        _validate_uuid4(self.value, "CycleSnapshotId")

    @classmethod
    def generate(cls) -> CycleSnapshotId:
        return cls(str(uuid.uuid4()))


# ── Projections / VOs ─────────────────────────────────────────────


@dataclass(frozen=True)
class CardSnapshot:
    """Projection de una Card completada, con los campos necesarios para
    metricas. Se usa como VO en CycleSnapshot y como input del calculator."""

    card_id: CardId
    area_id: AreaId | None
    project_id: ProjectId | None
    epic_id: EpicId | None
    size: CardSize | None
    actual_time_minutes: int
    created_at: Timestamp
    entered_workflow_at: Timestamp | None
    completed_at: Timestamp


@dataclass(frozen=True)
class CycleView:
    """Projection minima de un Cycle para el BC metrics."""

    id: CycleId
    space_id: SpaceId
    date_range: DateRange
    area_budgets: dict[AreaId, int]
    buffer_percentage: int
    state: str


@dataclass(frozen=True)
class CalibrationEntry:
    card_id: CardId
    estimated_minutes: int
    actual_minutes: int


@dataclass(frozen=True)
class MetricsBlock:
    """Bloque de metricas reutilizado en cada nivel del arbol (global,
    area, project, epic)."""

    total_cards_completed: int
    avg_cycle_time_minutes: float | None
    avg_lead_time_minutes: float | None
    consumed_minutes: int
    calibration_entries: list[CalibrationEntry]


@dataclass(frozen=True)
class ProjectMetrics:
    project_id: ProjectId
    metrics: MetricsBlock
    epics: dict[EpicId, MetricsBlock]


@dataclass(frozen=True)
class AreaMetrics:
    area_id: AreaId
    budget_minutes: int
    metrics: MetricsBlock
    projects: dict[ProjectId, ProjectMetrics]
