from fastapi import APIRouter, Depends, Query

from sigma_core.metrics.application.queries.get_metrics import (
    GetMetrics,
    GetMetricsQuery,
)
from sigma_core.metrics.application.queries.get_snapshot import (
    GetSnapshot,
    GetSnapshotQuery,
)
from sigma_core.planning.domain.value_objects import CycleId
from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_rest.dependencies import (
    get_metrics_card_reader,
    get_metrics_cycle_reader,
    get_metrics_space_reader,
    get_cycle_summary_repo,
    get_cycle_snapshot_repo,
)
from sigma_rest.mappers.metrics_mappers import (
    metrics_result_to_response,
    snapshot_to_response,
)


router = APIRouter(prefix="/spaces/{space_id}/metrics", tags=["metrics"])


@router.get("")
async def get_metrics(
    space_id: str,
    cycle_id: str | None = Query(default=None),
    cycle_reader=Depends(get_metrics_cycle_reader),
    summary_repo=Depends(get_cycle_summary_repo),
    card_reader=Depends(get_metrics_card_reader),
    space_reader=Depends(get_metrics_space_reader),
):
    query = GetMetrics(
        cycle_reader=cycle_reader,
        summary_repo=summary_repo,
        card_reader=card_reader,
        space_reader=space_reader,
    )
    result = await query.execute(
        GetMetricsQuery(
            space_id=SpaceId(space_id),
            cycle_id=CycleId(cycle_id) if cycle_id else None,
        )
    )
    return metrics_result_to_response(result)


@router.get("/snapshots/{cycle_id}")
async def get_snapshot(
    space_id: str,
    cycle_id: str,
    snapshot_repo=Depends(get_cycle_snapshot_repo),
):
    query = GetSnapshot(snapshot_repo=snapshot_repo)
    result = await query.execute(
        GetSnapshotQuery(cycle_id=CycleId(cycle_id))
    )
    return snapshot_to_response(result)
