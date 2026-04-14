"""Mappers domain → response para metrics."""
from sigma_core.metrics.application.queries.get_metrics import MetricsResult
from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.domain.value_objects import (
    AreaMetrics,
    CalibrationEntry,
    CardSnapshot,
    MetricsBlock,
    ProjectMetrics,
)
from sigma_rest.schemas.metrics_schemas import (
    AreaMetricsResponse,
    CalibrationEntryResponse,
    CardSnapshotResponse,
    MetricsBlockResponse,
    MetricsResponse,
    ProjectMetricsResponse,
    SnapshotResponse,
)


def _calibration_to_response(e: CalibrationEntry) -> CalibrationEntryResponse:
    return CalibrationEntryResponse(
        card_id=e.card_id.value,
        estimated_minutes=e.estimated_minutes,
        actual_minutes=e.actual_minutes,
    )


def _block_to_response(block: MetricsBlock) -> MetricsBlockResponse:
    return MetricsBlockResponse(
        total_cards_completed=block.total_cards_completed,
        avg_cycle_time_minutes=block.avg_cycle_time_minutes,
        avg_lead_time_minutes=block.avg_lead_time_minutes,
        consumed_minutes=block.consumed_minutes,
        actual_consumed_minutes=block.actual_consumed_minutes,
        calibration_entries=[
            _calibration_to_response(e) for e in block.calibration_entries
        ],
    )


def _project_to_response(pm: ProjectMetrics) -> ProjectMetricsResponse:
    return ProjectMetricsResponse(
        project_id=pm.project_id.value,
        metrics=_block_to_response(pm.metrics),
        epics={
            eid.value: _block_to_response(block)
            for eid, block in pm.epics.items()
        },
    )


def _area_to_response(am: AreaMetrics) -> AreaMetricsResponse:
    return AreaMetricsResponse(
        area_id=am.area_id.value,
        budget_minutes=am.budget_minutes,
        metrics=_block_to_response(am.metrics),
        projects={
            pid.value: _project_to_response(pm)
            for pid, pm in am.projects.items()
        },
    )


def metrics_result_to_response(result: MetricsResult) -> MetricsResponse:
    return MetricsResponse(
        cycle_id=result.cycle_id.value,
        space_id=result.space_id.value,
        date_range={
            "start": result.date_range.start.isoformat(),
            "end": result.date_range.end.isoformat(),
        },
        computed_at=result.computed_at.value.isoformat(),
        source=result.source,
        global_metrics=_block_to_response(result.global_metrics),
        areas={
            aid.value: _area_to_response(am)
            for aid, am in result.areas.items()
        },
    )


def _card_snapshot_to_response(cs: CardSnapshot) -> CardSnapshotResponse:
    return CardSnapshotResponse(
        card_id=cs.card_id.value,
        area_id=cs.area_id.value if cs.area_id else None,
        project_id=cs.project_id.value if cs.project_id else None,
        epic_id=cs.epic_id.value if cs.epic_id else None,
        size=cs.size.value if cs.size else None,
        actual_time_minutes=cs.actual_time_minutes,
        created_at=cs.created_at.value.isoformat(),
        entered_workflow_at=(
            cs.entered_workflow_at.value.isoformat()
            if cs.entered_workflow_at
            else None
        ),
        completed_at=cs.completed_at.value.isoformat(),
    )


def snapshot_to_response(snapshot: CycleSnapshot) -> SnapshotResponse:
    return SnapshotResponse(
        id=snapshot.id.value,
        cycle_id=snapshot.cycle_id.value,
        space_id=snapshot.space_id.value,
        date_range={
            "start": snapshot.date_range.start.isoformat(),
            "end": snapshot.date_range.end.isoformat(),
        },
        buffer_percentage=snapshot.buffer_percentage,
        area_budgets={
            aid.value: minutes
            for aid, minutes in snapshot.area_budgets.items()
        },
        size_mapping=snapshot.size_mapping,
        cards=[_card_snapshot_to_response(c) for c in snapshot.cards],
        created_at=snapshot.created_at.value.isoformat(),
    )
