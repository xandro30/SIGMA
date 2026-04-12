from datetime import date as date_cls

from fastapi import APIRouter, Depends, Query

from sigma_core.planning.application.queries.card_eta import (
    GetCardEta,
    GetCardEtaQuery,
)
from sigma_core.planning.application.queries.space_capacity import (
    GetSpaceCapacity,
    GetSpaceCapacityQuery,
)
from sigma_core.shared_kernel.value_objects import CardId, SpaceId
from sigma_rest.dependencies import (
    get_card_reader,
    get_cycle_repo,
    get_space_reader,
)
from sigma_rest.schemas.planning_queries_schemas import (
    AreaCapacityResponse,
    CardEtaResponse,
    SpaceCapacityResponse,
)


router = APIRouter(tags=["planning-queries"])


@router.get("/spaces/{space_id}/capacity")
async def get_space_capacity(
    space_id: str,
    reference_date: date_cls | None = Query(default=None),
    cycle_repo=Depends(get_cycle_repo),
    card_reader=Depends(get_card_reader),
    space_reader=Depends(get_space_reader),
):
    use_case = GetSpaceCapacity(cycle_repo, card_reader, space_reader)
    result = await use_case.execute(
        GetSpaceCapacityQuery(
            space_id=SpaceId(space_id),
            reference_date=reference_date,
        )
    )
    return SpaceCapacityResponse(
        cycle_id=result.cycle_id.value,
        date_range={
            "start": result.date_range.start.isoformat(),
            "end": result.date_range.end.isoformat(),
        },
        buffer_percentage=result.buffer_percentage,
        areas=[
            AreaCapacityResponse(
                area_id=a.area_id.value,
                budget_minutes=a.budget_minutes,
                consumed_minutes=a.consumed_minutes,
                remaining_minutes=a.remaining_minutes,
            )
            for a in result.areas
        ],
    )


@router.get("/cards/{card_id}/eta")
async def get_card_eta(
    card_id: str,
    reference_date: date_cls = Query(...),
    cycle_repo=Depends(get_cycle_repo),
    card_reader=Depends(get_card_reader),
    space_reader=Depends(get_space_reader),
):
    use_case = GetCardEta(cycle_repo, card_reader, space_reader)
    result = await use_case.execute(
        GetCardEtaQuery(
            card_id=CardId(card_id),
            reference_date=reference_date,
        )
    )
    return CardEtaResponse(
        card_id=result.card_id.value,
        estimated_minutes=result.estimated_minutes,
        daily_capacity_minutes=result.daily_capacity_minutes,
        raw_completion_date=result.raw_completion_date.isoformat(),
        buffered_completion_date=result.buffered_completion_date.isoformat(),
    )
