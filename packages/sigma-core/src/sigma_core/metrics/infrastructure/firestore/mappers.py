"""Mappers Firestore para el BC metrics.

Schemas:

cycle_summary:
  {id, cycle_id, space_id,
   date_range: {start, end},
   global_metrics: MetricsBlockDict,
   areas: {<area_id>: AreaMetricsDict},
   created_at}

cycle_snapshot:
  {id, cycle_id, space_id,
   date_range: {start, end},
   buffer_percentage, area_budgets: {<area_id>: int},
   size_mapping: {<size>: int} | null,
   cards: [CardSnapshotDict],
   created_at}
"""
from __future__ import annotations

from datetime import date
from typing import Any

from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.metrics.domain.value_objects import (
    AreaMetrics,
    CalibrationEntry,
    CardSnapshot,
    CycleSnapshotId,
    CycleSummaryId,
    CycleView,
    MetricsBlock,
    ProjectMetrics,
)
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


def snapshot_data(doc) -> dict[str, Any]:
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


def _ts_to(ts: Timestamp):
    return ts.value


def _ts_from(dt) -> Timestamp:
    return Timestamp(dt.astimezone(get_app_timezone()))


def _date_to(d: date) -> str:
    return d.isoformat()


def _date_from(s: str) -> date:
    return date.fromisoformat(s)


# ── MetricsBlock ──────────────────────────────────────────────────


def _block_to_dict(block: MetricsBlock) -> dict[str, Any]:
    return {
        "total_cards_completed": block.total_cards_completed,
        "avg_cycle_time_minutes": block.avg_cycle_time_minutes,
        "avg_lead_time_minutes": block.avg_lead_time_minutes,
        "consumed_minutes": block.consumed_minutes,
        "calibration_entries": [
            {
                "card_id": e.card_id.value,
                "estimated_minutes": e.estimated_minutes,
                "actual_minutes": e.actual_minutes,
            }
            for e in block.calibration_entries
        ],
    }


def _block_from_dict(data: dict[str, Any]) -> MetricsBlock:
    return MetricsBlock(
        total_cards_completed=data["total_cards_completed"],
        avg_cycle_time_minutes=data["avg_cycle_time_minutes"],
        avg_lead_time_minutes=data["avg_lead_time_minutes"],
        consumed_minutes=data["consumed_minutes"],
        calibration_entries=[
            CalibrationEntry(
                card_id=CardId(e["card_id"]),
                estimated_minutes=e["estimated_minutes"],
                actual_minutes=e["actual_minutes"],
            )
            for e in data["calibration_entries"]
        ],
    )


# ── ProjectMetrics / AreaMetrics ──────────────────────────────────


def _project_metrics_to_dict(pm: ProjectMetrics) -> dict[str, Any]:
    return {
        "project_id": pm.project_id.value,
        "metrics": _block_to_dict(pm.metrics),
        "epics": {
            eid.value: _block_to_dict(block)
            for eid, block in pm.epics.items()
        },
    }


def _project_metrics_from_dict(data: dict[str, Any]) -> ProjectMetrics:
    return ProjectMetrics(
        project_id=ProjectId(data["project_id"]),
        metrics=_block_from_dict(data["metrics"]),
        epics={
            EpicId(eid): _block_from_dict(block)
            for eid, block in data["epics"].items()
        },
    )


def _area_metrics_to_dict(am: AreaMetrics) -> dict[str, Any]:
    return {
        "area_id": am.area_id.value,
        "budget_minutes": am.budget_minutes,
        "metrics": _block_to_dict(am.metrics),
        "projects": {
            pid.value: _project_metrics_to_dict(pm)
            for pid, pm in am.projects.items()
        },
    }


def _area_metrics_from_dict(data: dict[str, Any]) -> AreaMetrics:
    return AreaMetrics(
        area_id=AreaId(data["area_id"]),
        budget_minutes=data["budget_minutes"],
        metrics=_block_from_dict(data["metrics"]),
        projects={
            ProjectId(pid): _project_metrics_from_dict(pm)
            for pid, pm in data["projects"].items()
        },
    )


# ── CycleSummary ──────────────────────────────────────────────────


def cycle_summary_to_dict(summary: CycleSummary) -> dict[str, Any]:
    return {
        "id": summary.id.value,
        "cycle_id": summary.cycle_id.value,
        "space_id": summary.space_id.value,
        "date_range": {
            "start": _date_to(summary.date_range.start),
            "end": _date_to(summary.date_range.end),
        },
        "global_metrics": _block_to_dict(summary.global_metrics),
        "areas": {
            aid.value: _area_metrics_to_dict(am)
            for aid, am in summary.areas.items()
        },
        "created_at": _ts_to(summary.created_at),
    }


def cycle_summary_from_dict(data: dict[str, Any]) -> CycleSummary:
    return CycleSummary(
        id=CycleSummaryId(data["id"]),
        cycle_id=CycleId(data["cycle_id"]),
        space_id=SpaceId(data["space_id"]),
        date_range=DateRange(
            start=_date_from(data["date_range"]["start"]),
            end=_date_from(data["date_range"]["end"]),
        ),
        global_metrics=_block_from_dict(data["global_metrics"]),
        areas={
            AreaId(aid): _area_metrics_from_dict(am)
            for aid, am in data["areas"].items()
        },
        created_at=_ts_from(data["created_at"]),
    )


# ── CycleSnapshot ─────────────────────────────────────────────────


def _card_snapshot_to_dict(cs: CardSnapshot) -> dict[str, Any]:
    return {
        "card_id": cs.card_id.value,
        "area_id": cs.area_id.value if cs.area_id else None,
        "project_id": cs.project_id.value if cs.project_id else None,
        "epic_id": cs.epic_id.value if cs.epic_id else None,
        "size": cs.size.value if cs.size else None,
        "actual_time_minutes": cs.actual_time_minutes,
        "created_at": _ts_to(cs.created_at),
        "entered_workflow_at": (
            _ts_to(cs.entered_workflow_at) if cs.entered_workflow_at else None
        ),
        "completed_at": _ts_to(cs.completed_at),
    }


def _card_snapshot_from_dict(data: dict[str, Any]) -> CardSnapshot:
    return CardSnapshot(
        card_id=CardId(data["card_id"]),
        area_id=AreaId(data["area_id"]) if data["area_id"] else None,
        project_id=(
            ProjectId(data["project_id"]) if data["project_id"] else None
        ),
        epic_id=EpicId(data["epic_id"]) if data["epic_id"] else None,
        size=CardSize(data["size"]) if data["size"] else None,
        actual_time_minutes=data["actual_time_minutes"],
        created_at=_ts_from(data["created_at"]),
        entered_workflow_at=(
            _ts_from(data["entered_workflow_at"])
            if data["entered_workflow_at"]
            else None
        ),
        completed_at=_ts_from(data["completed_at"]),
    )


def cycle_snapshot_to_dict(snapshot: CycleSnapshot) -> dict[str, Any]:
    return {
        "id": snapshot.id.value,
        "cycle_id": snapshot.cycle_id.value,
        "space_id": snapshot.space_id.value,
        "date_range": {
            "start": _date_to(snapshot.date_range.start),
            "end": _date_to(snapshot.date_range.end),
        },
        "buffer_percentage": snapshot.buffer_percentage,
        "area_budgets": {
            aid.value: minutes
            for aid, minutes in snapshot.area_budgets.items()
        },
        "size_mapping": snapshot.size_mapping,
        "cards": [_card_snapshot_to_dict(c) for c in snapshot.cards],
        "created_at": _ts_to(snapshot.created_at),
    }


def cycle_snapshot_from_dict(data: dict[str, Any]) -> CycleSnapshot:
    return CycleSnapshot(
        id=CycleSnapshotId(data["id"]),
        cycle_id=CycleId(data["cycle_id"]),
        space_id=SpaceId(data["space_id"]),
        date_range=DateRange(
            start=_date_from(data["date_range"]["start"]),
            end=_date_from(data["date_range"]["end"]),
        ),
        buffer_percentage=data["buffer_percentage"],
        area_budgets={
            AreaId(aid): minutes
            for aid, minutes in data["area_budgets"].items()
        },
        size_mapping=data["size_mapping"],
        cards=[_card_snapshot_from_dict(c) for c in data["cards"]],
        created_at=_ts_from(data["created_at"]),
    )
