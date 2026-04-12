from datetime import date as date_cls

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from sigma_core.planning.application.use_cases.day.add_block import (
    AddBlockToDay,
    AddBlockToDayCommand,
)
from sigma_core.planning.application.use_cases.day.clear_blocks import (
    ClearDayBlocks,
    ClearDayBlocksCommand,
)
from sigma_core.planning.application.use_cases.day.create_day import (
    CreateDay,
    CreateDayCommand,
)
from sigma_core.planning.application.use_cases.day.remove_block import (
    RemoveBlockFromDay,
    RemoveBlockFromDayCommand,
)
from sigma_core.planning.application.use_cases.day.update_block import (
    UpdateBlockInDay,
    UpdateBlockInDayCommand,
)
from sigma_core.planning.domain.errors import DayNotFoundError
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DateRange,
    DayId,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp
from sigma_rest.dependencies import get_day_repo
from sigma_rest.mappers.day_mappers import day_to_response
from sigma_rest.routers._helpers import require_day
from sigma_rest.schemas.day_schemas import (
    AddBlockRequest,
    CreateDayRequest,
    UpdateBlockRequest,
)


router = APIRouter(prefix="/spaces/{space_id}/days", tags=["days"])


MAX_DAYS_RANGE = 365  # límite del adaptador HTTP, no del dominio


@router.post("", status_code=201)
async def create_day(
    space_id: str,
    body: CreateDayRequest,
    day_repo=Depends(get_day_repo),
):
    use_case = CreateDay(day_repo)
    day_id = await use_case.execute(
        CreateDayCommand(space_id=SpaceId(space_id), target_date=body.date)
    )
    day = await require_day(day_repo, day_id)
    return day_to_response(day)


@router.get("/by-date/{target_date}")
async def get_day_by_date(
    space_id: str,
    target_date: date_cls,
    day_repo=Depends(get_day_repo),
):
    day = await day_repo.get_by_space_and_date(
        SpaceId(space_id), target_date
    )
    if day is None:
        raise DayNotFoundError(
            f"No day for space {space_id} on {target_date.isoformat()}"
        )
    return day_to_response(day)


@router.get("/by-range")
async def list_days_in_range(
    space_id: str,
    start: date_cls = Query(...),
    end: date_cls = Query(...),
    day_repo=Depends(get_day_repo),
):
    date_range = DateRange(start=start, end=end)
    if date_range.days_count() > MAX_DAYS_RANGE:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "date_range_too_large",
                "message": (
                    f"date range spans {date_range.days_count()} days; "
                    f"maximum allowed is {MAX_DAYS_RANGE}"
                ),
                "max_days": MAX_DAYS_RANGE,
            },
        )
    days = await day_repo.list_by_space_and_range(
        SpaceId(space_id), date_range
    )
    return {"days": [day_to_response(d) for d in days]}


@router.get("/{day_id}")
async def get_day(
    space_id: str,
    day_id: str,
    day_repo=Depends(get_day_repo),
):
    day = await require_day(day_repo, DayId(day_id))
    return day_to_response(day)


@router.post("/{day_id}/blocks", status_code=201)
async def add_block(
    space_id: str,
    day_id: str,
    body: AddBlockRequest,
    day_repo=Depends(get_day_repo),
):
    use_case = AddBlockToDay(day_repo)
    await use_case.execute(
        AddBlockToDayCommand(
            day_id=DayId(day_id),
            start_at=Timestamp(body.start_at),
            duration=Minutes(body.duration),
            area_id=AreaId(body.area_id) if body.area_id else None,
            notes=body.notes,
        )
    )
    day = await require_day(day_repo, DayId(day_id))
    return day_to_response(day)


@router.patch("/{day_id}/blocks/{block_id}")
async def update_block(
    space_id: str,
    day_id: str,
    block_id: str,
    body: UpdateBlockRequest,
    day_repo=Depends(get_day_repo),
):
    use_case = UpdateBlockInDay(day_repo)
    await use_case.execute(
        UpdateBlockInDayCommand(
            day_id=DayId(day_id),
            block_id=BlockId(block_id),
            start_at=(
                Timestamp(body.start_at) if body.start_at is not None else None
            ),
            duration=(
                Minutes(body.duration) if body.duration is not None else None
            ),
            area_id_set=body.area_id_set,
            area_id=AreaId(body.area_id) if body.area_id is not None else None,
            notes=body.notes,
        )
    )
    day = await require_day(day_repo, DayId(day_id))
    return day_to_response(day)


@router.delete("/{day_id}/blocks/{block_id}")
async def remove_block(
    space_id: str,
    day_id: str,
    block_id: str,
    day_repo=Depends(get_day_repo),
):
    use_case = RemoveBlockFromDay(day_repo)
    await use_case.execute(
        RemoveBlockFromDayCommand(
            day_id=DayId(day_id), block_id=BlockId(block_id)
        )
    )
    day = await require_day(day_repo, DayId(day_id))
    return day_to_response(day)


@router.delete("/{day_id}/blocks", status_code=204)
async def clear_blocks(
    space_id: str,
    day_id: str,
    day_repo=Depends(get_day_repo),
):
    use_case = ClearDayBlocks(day_repo)
    await use_case.execute(ClearDayBlocksCommand(day_id=DayId(day_id)))
    return Response(status_code=204)
